// my_driver: pure-pursuit steering + curvature/braking speed profile.
//
// Idea in 4 lines:
//   1. Find where the car is along the path (arc length s), moving forward only.
//   2. Steer toward a point `lookahead` metres further along the path (pure pursuit).
//   3. Speed limit at every upcoming node: v^2 <= lat_accel / curvature, and
//      v^2 <= 2 * brake_decel * distance_to_finish.  Command the smallest limit.
//   4. At the finish command 0; the 5 m free stop zone lets us aim slightly past it.
//   5. (2026-11-19) Prediction: the car reacts about 0.15 s late, so steer from where the car WILL be.
//      A small bicycle model steps the pose forward `predict_time` s, with the wheel following the last
//      command with a delay (time constant `steer_tau`, at most `steer_rate` rad/s). predict_time 0 = off.
//   6. (2026-11-19) Steering modes from 2025-2026 papers (param steer_mode):
//      pp          pure pursuit (default), optional curvature feed-forward blend (ff_gain, Kapania & Gerdes 2015)
//      stanley     Stanley at the front axle: delta = psi + atan(K e / (K_prot + v))      (DLR 2026 eq. 3.4, Hoffmann 2007)
//                  with stanley_pred_steps > 0: predictive Stanley, weighted sum over a horizon (DLR 2026 eq. 3.12-3.14)
//      stanley_ff  rear-axle Stanley + feed-forward atan(L kappa) at v*ff_time ahead      (DLR 2026 enhanced Stanley)
//      lqr         kinematic MPC without constraints (= infinite-horizon LQR) on the path-error model with the
//                  steering lag as a state, + curvature feed-forward      (idea of MAP2 / LPV-MPC / FS Driverless 2026)
//                  state x = [e, psi_e, steer - steer_ff];  e' = v psi_e;  psi_e' = v/L (steer - steer_ff);
//                  steer' = (u - steer)/tau.  u = steer_ff(ahead) - K x,  K from the discrete Riccati equation.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/empty.hpp"
#include "thr_sim_msgs/msg/ref_path.hpp"
#include "thr_sim_msgs/msg/veh_ctrl.hpp"
#include "thr_sim_msgs/msg/veh_state.hpp"

using namespace std::chrono_literals;
using thr_sim_msgs::msg::RefPath;
using thr_sim_msgs::msg::VehCtrl;
using thr_sim_msgs::msg::VehState;

namespace
{
double wrap(double a) {return std::atan2(std::sin(a), std::cos(a));}

struct Pt
{
  double x, y;
};

struct Pose
{
  double x, y, yaw;
};

struct Location
{
  size_t index;  // nearest node (used to advance progress)
  double s;      // arc length of the car's projection on the path [m]
};
}  // namespace

class Driver : public rclcpp::Node
{
public:
  Driver()
  : Node("my_driver")
  {
    // All tuning values are ROS parameters: change with --ros-args -p name:=value
    cruise_ = declare_parameter("cruise_speed", 12.0);       // top speed [m/s]
    a_lat_ = declare_parameter("lat_accel", 3.0);            // allowed v^2*kappa [m/s^2]
    brake_ = declare_parameter("brake_decel", 3.5);          // planned braking [m/s^2]
    stop_aim_ = declare_parameter("stop_aim", 1.5);          // plan to stop this far PAST finish [m]
    ld_base_ = declare_parameter("lookahead_base", 2.5);     // [m]
    ld_gain_ = declare_parameter("lookahead_gain", 0.4);     // extra lookahead per m/s [s]
    wheelbase_ = declare_parameter("wheelbase", 2.5);        // [m]
    max_steer_ = declare_parameter("max_steer", 0.6);        // [rad]
    predict_ = declare_parameter("predict_time", 0.0);       // look this far into the future [s], 0 = off
    steer_tau_ = declare_parameter("steer_tau", 0.10);       // wheel follows the command with this lag [s]
    steer_rate_ = declare_parameter("steer_rate", 1.0);      // wheel turns at most this fast [rad/s]
    use_age_ = declare_parameter("predict_add_age", true);   // also cover the age of the pose message
    steer_pi_ = declare_parameter("steer_model", std::string("lag")) == "pi";  // lag | pi (the sim's real PI loop)
    st_kp_ = declare_parameter("steer_kp", 4.0);             // sim.yaml steer loop (zeta 0.28, wn 7.1 rad/s)
    st_ki_ = declare_parameter("steer_ki", 50.0);
    stop_damp_ = declare_parameter("stop_damp", 0.0);        // after the finish: cancel backward roll, 0 = off
    mode_ = declare_parameter("steer_mode", std::string("pp"));  // pp | stanley | stanley_ff
    st_k_ = declare_parameter("stanley_k", 2.0);             // gain on the sideways error [1/s]
    st_soft_ = declare_parameter("stanley_soft", 1.0);       // K_prot: keeps the gain finite at low speed [m/s]
    st_yaw_ = declare_parameter("stanley_yaw_damp", 0.0);    // yaw-rate damping gain (Hoffmann 2007), 0 = off
    st_n_ = declare_parameter("stanley_pred_steps", 0);      // predictive Stanley horizon steps, 0 = plain Stanley
    st_dt_ = declare_parameter("stanley_pred_dt", 0.05);     // [s] per predicted step
    st_decay_ = declare_parameter("stanley_pred_decay", 0.7);  // weight of step k = decay^k (then normalised)
    ff_time_ = declare_parameter("ff_time", 0.10);           // feed-forward point = v * ff_time ahead [s]
    ff_gain_ = declare_parameter("ff_gain", 0.0);            // pp only: blend of feed-forward steering, 0 = off
    lqr_qe_ = declare_parameter("lqr_q_e", 1.0);             // cost on sideways error [1/m^2]
    lqr_qpsi_ = declare_parameter("lqr_q_psi", 1.0);         // cost on heading error [1/rad^2]
    lqr_r_ = declare_parameter("lqr_r", 1.0);                // cost on steering command [1/rad^2]
    lqr_dt_ = declare_parameter("lqr_dt", 0.05);             // model step [s] (= control period)
    blend_lqr_ = declare_parameter("blend_lqr", 0.0);        // pp only: share of LQR steering mixed in, 0 = off
    bang_ = declare_parameter("bang_brake", false);          // brake to the finish at FULL decel (command 0) at the last moment
    bang_decel_ = declare_parameter("bang_decel", 6.0);      // decel used to find the brake point [m/s^2] (car limit 6)
    bang_lead_ = declare_parameter("bang_lead", 0.0);        // extra brake distance per m/s, on top of one period [s]
    bang_neg_ = declare_parameter("bang_cmd", -30.0);        // command while braking: very negative = full decel at once
    bang_release_ = declare_parameter("bang_release", 1.0);  // below this speed command 0 (do not reverse) [m/s]

    // /path is latched: transient-local so we still get it if we start late.
    auto path_qos = rclcpp::QoS(1).reliable().transient_local();
    path_sub_ = create_subscription<RefPath>(
      "/path", path_qos, [this](const RefPath & m) {on_path(m);});
    state_sub_ = create_subscription<VehState>(
      "/veh_state", 10, [this](const VehState & m) {state_ = m;});
    actual_sub_ = create_subscription<VehCtrl>(
      "/veh_actual", 10, [this](const VehCtrl & m) {
        v_actual_ = m.velocity;
        steer_actual_ = m.steer;
      });
    reset_sub_ = create_subscription<std_msgs::msg::Empty>(
      "/reset", 10, [this](const std_msgs::msg::Empty &) {on_reset();});
    publisher_ = create_publisher<VehCtrl>("/veh_ctrl", 10);
    const double hz = declare_parameter("control_hz", 20.0);   // control rate; 100 makes bang braking precise
    period_ = 1.0 / std::max(1.0, hz);
    timer_ = create_wall_timer(std::chrono::duration<double>(period_), [this]() {control();});  // always running
  }

private:
  // ---------------------------------------------------------------- callbacks
  void on_path(const RefPath & msg)
  {
    pts_.clear();
    s_.clear();
    kappa_.clear();
    kappa_s_.clear();
    progress_ = 0;
    braking_ = false;
    finish_ = msg.finish_index;
    if (msg.nodes.size() < 2 || finish_ >= msg.nodes.size()) {
      return;  // empty/invalid path = no task -> control() commands zero
    }
    for (const auto & p : msg.nodes) {
      pts_.push_back({p.x, p.y});
    }
    // cumulative arc length
    s_.assign(pts_.size(), 0.0);
    for (size_t i = 1; i < pts_.size(); ++i) {
      s_[i] = s_[i - 1] + std::hypot(pts_[i].x - pts_[i - 1].x, pts_[i].y - pts_[i - 1].y);
    }
    // curvature at each node from the heading change over +/- k nodes
    const size_t n = pts_.size(), k = 2;
    kappa_.assign(n, 0.0);
    kappa_s_.assign(n, 0.0);   // signed: + = path turns left
    for (size_t i = k; i + k < n; ++i) {
      const double h1 = std::atan2(pts_[i].y - pts_[i - k].y, pts_[i].x - pts_[i - k].x);
      const double h2 = std::atan2(pts_[i + k].y - pts_[i].y, pts_[i + k].x - pts_[i].x);
      const double ds = 0.5 * (s_[i + k] - s_[i - k]);
      kappa_s_[i] = ds > 1e-6 ? wrap(h2 - h1) / ds : 0.0;
      kappa_[i] = std::fabs(kappa_s_[i]);
    }
    for (size_t i = 0; i < std::min(k, n); ++i) {  // copy to the ends
      kappa_[i] = kappa_[std::min(k, n - 1)];
      kappa_[n - 1 - i] = kappa_[n - 1 - std::min(k, n - 1)];
      kappa_s_[i] = kappa_s_[std::min(k, n - 1)];
      kappa_s_[n - 1 - i] = kappa_s_[n - 1 - std::min(k, n - 1)];
    }
  }

  void on_reset()
  {
    // Forget progress and feedback, KEEP the path (/path and /reset can arrive in any order).
    state_.reset();
    v_actual_ = 0.0;
    steer_actual_ = 0.0;
    last_steer_ = 0.0;
    braking_ = false;
    pi_int_ = 0.0;
    progress_ = 0;
  }

  // ------------------------------------------------------------- prediction
  // Kinematic bicycle model (same as the simulator), stepped forward `horizon` seconds.
  // The wheel starts at its ACTUAL angle and moves toward the last command with a delay.
  // Move pose p (wheel angle st) forward `horizon` s at speed v while the wheel moves toward `target`.
  void roll(Pose & p, double & st, double target, double v, double horizon) const
  {
    const double dt = 0.005;
    double integ = pi_int_;   // copy of the estimated PI integral state
    for (double t = 0.0; t < horizon - 1e-9; t += dt) {
      const double h = std::min(dt, horizon - t);
      if (steer_pi_) {        // same law as the simulator: rate = clamp(kp e + ki int e), anti-windup
        const double e = target - st;
        const double ni = integ + e * h;
        const double u = st_kp_ * e + st_ki_ * ni;
        const double rate = std::clamp(u, -steer_rate_, steer_rate_);
        if (rate == u) {integ = ni;}
        st += rate * h;
      } else {
        const double want = steer_tau_ > 1e-6 ? (target - st) * h / steer_tau_ : target - st;
        st += std::clamp(want, -steer_rate_ * h, steer_rate_ * h);
      }
      p.x += v * std::cos(p.yaw) * h;
      p.y += v * std::sin(p.yaw) * h;
      p.yaw = wrap(p.yaw + v / wheelbase_ * std::tan(st) * h);
    }
  }

  Pose predict(double horizon, double * st_out = nullptr) const
  {
    Pose p{state_->x, state_->y, state_->yaw};
    double st = steer_actual_;
    roll(p, st, last_steer_, v_actual_, horizon);
    if (st_out) {*st_out = st;}
    return p;
  }

  // LQR gain for x = [e, psi_e, steer_dev], discrete model at speed v (Euler, step lqr_dt), steering lag steer_tau.
  void lqr_gain(double v, double K[3]) const
  {
    const double dt = lqr_dt_, tau = std::max(steer_tau_, 1e-3), L = wheelbase_;
    const double A[3][3] = {{1.0, v * dt, 0.0}, {0.0, 1.0, v / L * dt}, {0.0, 0.0, 1.0 - dt / tau}};
    const double B[3] = {0.0, 0.0, dt / tau};
    double P[3][3] = {{lqr_qe_, 0, 0}, {0, lqr_qpsi_, 0}, {0, 0, 0}};
    for (int it = 0; it < 300; ++it) {   // value iteration of the Riccati equation
      double PA[3][3] = {}, PB[3] = {};
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          for (int k = 0; k < 3; ++k) {PA[i][j] += P[i][k] * A[k][j];}
          PB[i] += P[i][j] * B[j];
        }
      }
      double BPB = 0.0, BPA[3] = {};
      for (int i = 0; i < 3; ++i) {
        BPB += B[i] * PB[i];
        for (int j = 0; j < 3; ++j) {BPA[j] += B[i] * PA[i][j];}
      }
      const double inv = 1.0 / (lqr_r_ + BPB);
      double Pn[3][3];
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
          double APA = 0.0;
          for (int k = 0; k < 3; ++k) {APA += A[k][i] * PA[k][j];}
          Pn[i][j] = APA - BPA[i] * BPA[j] * inv;
        }
      }
      Pn[0][0] += lqr_qe_;
      Pn[1][1] += lqr_qpsi_;
      std::copy(&Pn[0][0], &Pn[0][0] + 9, &P[0][0]);
      if (it == 299) {for (int j = 0; j < 3; ++j) {K[j] = BPA[j] * inv;}}
    }
  }

  double steer_lqr(const Pose & p, double st, double v)
  {
    const Location l = locate(p.x, p.y);
    const size_t from = l.index > 0 ? l.index - 1 : 0;
    const Pt q = point_at(l.s, from);
    const double head = heading_at(l.s, from);
    const double e = std::cos(head) * (p.y - q.y) - std::sin(head) * (p.x - q.x);   // + = left of path
    const double psi = wrap(p.yaw - head);                                          // + = pointing left
    const double ff_now = std::atan(wheelbase_ * kappa_at(l.s, from));
    const double ff_ahead = std::atan(wheelbase_ * kappa_at(l.s + std::fabs(v) * ff_time_, from));
    double K[3];
    lqr_gain(std::max(std::fabs(v), 1.0), K);
    const double u = ff_ahead - (K[0] * e + K[1] * psi + K[2] * (st - ff_now));
    return std::clamp(u, -max_steer_, max_steer_);
  }

  // ------------------------------------------------------------- path helpers for Stanley / feed-forward
  double heading_at(double s_target, size_t from) const
  {
    size_t j = from;
    while (j + 1 < pts_.size() && s_[j + 1] < s_target) {++j;}
    if (j + 1 >= pts_.size()) {j = pts_.size() - 2;}
    return std::atan2(pts_[j + 1].y - pts_[j].y, pts_[j + 1].x - pts_[j].x);
  }

  double kappa_at(double s_target, size_t from) const
  {
    size_t j = from;
    while (j + 1 < pts_.size() && s_[j + 1] < s_target) {++j;}
    return kappa_s_[j];
  }

  // Stanley at reference point (x, y) of a car with heading yaw: heading error + atan(K e / (K_prot + v)).
  // e > 0 when the reference point is LEFT of the path, so then we steer right (minus).
  double stanley_terms(double x, double y, double yaw, double v, size_t * idx = nullptr, double * s_out = nullptr)
  {
    const Location l = locate(x, y);
    const size_t from = l.index > 0 ? l.index - 1 : 0;
    const Pt q = point_at(l.s, from);
    const double head = heading_at(l.s, from);
    const double e = std::cos(head) * (y - q.y) - std::sin(head) * (x - q.x);
    if (idx) {*idx = from;}
    if (s_out) {*s_out = l.s;}
    return wrap(head - yaw) - std::atan(st_k_ * e / (st_soft_ + std::fabs(v)));
  }

  double stanley_front(const Pose & p, double v)
  {
    size_t idx = 0;
    double s = 0.0;
    double d = stanley_terms(p.x + wheelbase_ * std::cos(p.yaw), p.y + wheelbase_ * std::sin(p.yaw), p.yaw, v, &idx, &s);
    if (st_yaw_ > 0.0) {  // yaw-rate damping: expected (path) yaw rate minus the car's yaw rate
      d += st_yaw_ * (v * kappa_at(s, idx) - v / wheelbase_ * std::tan(steer_actual_));
    }
    return std::clamp(d, -max_steer_, max_steer_);
  }

  double steer_stanley(const Pose & p0, double v)
  {
    if (st_n_ <= 0) {return stanley_front(p0, v);}
    // predictive Stanley: Stanley on the current and N predicted states, weighted sum (weights decay, sum 1)
    Pose p = p0;
    double st = steer_actual_, sum = 0.0, wsum = 0.0, w = 1.0;
    for (int k = 0; k <= st_n_; ++k) {
      const double d = stanley_front(p, v);
      sum += w * d;
      wsum += w;
      w *= st_decay_;
      roll(p, st, d, v, st_dt_);
    }
    return std::clamp(sum / wsum, -max_steer_, max_steer_);
  }

  double steer_stanley_ff(const Pose & p, double v)
  {
    size_t idx = 0;
    double s = 0.0;
    const double fb = stanley_terms(p.x, p.y, p.yaw, v, &idx, &s);   // rear axle
    const double ff = std::atan(wheelbase_ * kappa_at(s + std::fabs(v) * ff_time_, idx));
    return std::clamp(ff + fb, -max_steer_, max_steer_);
  }

  // ------------------------------------------------------------- geometry
  // Project the car on the path. Search only ahead of the last progress, so the
  // circle (start == finish) can never jump back or ahead.
  Location locate(double x, double y)
  {
    const size_t n = pts_.size();
    const size_t hi = std::min(n - 1, progress_ + 80);  // 80 nodes = 40 m window
    size_t best = progress_;
    double best_d2 = 1e18;
    for (size_t i = progress_; i <= hi; ++i) {
      const double d2 = (pts_[i].x - x) * (pts_[i].x - x) + (pts_[i].y - y) * (pts_[i].y - y);
      if (d2 < best_d2) {
        best_d2 = d2;
        best = i;
      }
    }
    // refine: project onto the two segments touching the nearest node
    double best_s = s_[best], seg_d2 = best_d2;
    for (size_t j = (best > 0 ? best - 1 : 0); j <= best && j + 1 < n; ++j) {
      const double dx = pts_[j + 1].x - pts_[j].x, dy = pts_[j + 1].y - pts_[j].y;
      const double len2 = dx * dx + dy * dy;
      const double t =
        len2 > 1e-12 ? std::clamp(((x - pts_[j].x) * dx + (y - pts_[j].y) * dy) / len2, 0.0, 1.0) :
        0.0;
      const double px = pts_[j].x + t * dx - x, py = pts_[j].y + t * dy - y;
      const double d2 = px * px + py * py;
      if (d2 <= seg_d2) {
        seg_d2 = d2;
        best_s = s_[j] + t * std::sqrt(len2);
      }
    }
    return {best, best_s};
  }

  Pt point_at(double s_target, size_t from) const
  {
    size_t j = from;
    while (j + 1 < pts_.size() && s_[j + 1] < s_target) {++j;}
    if (j + 1 >= pts_.size()) {return pts_.back();}
    const double seg = s_[j + 1] - s_[j];
    const double t = seg > 1e-9 ? (s_target - s_[j]) / seg : 0.0;
    return {pts_[j].x + t * (pts_[j + 1].x - pts_[j].x),
      pts_[j].y + t * (pts_[j + 1].y - pts_[j].y)};
  }

  // ------------------------------------------------------------------ control
  void control()
  {
    double velocity = 0.0, steer = 0.0;  // default: stand still

    if (!pts_.empty() && state_) {
      const Location loc = locate(state_->x, state_->y);
      progress_ = std::max(progress_, loc.index);
      const double remaining = s_[finish_] - loc.s;  // >0 before the finish line

      // --- steering: pure pursuit  delta = atan(2 L sin(alpha) / ld), from the PREDICTED pose
      double horizon = predict_;
      if (predict_ > 0.0 && use_age_) {  // the pose message is already a little old
        const double age = (now() - rclcpp::Time(state_->header.stamp)).seconds();
        horizon += std::clamp(age, 0.0, 0.1);
      }
      if (steer_pi_) {        // keep our copy of the sim's PI integral in step with the real loop
        const double e = last_steer_ - steer_actual_;
        const double ni = pi_int_ + e * period_;
        if (std::fabs(st_kp_ * e + st_ki_ * ni) <= steer_rate_) {pi_int_ = ni;}
      }
      double st_pred = steer_actual_;
      const Pose p = horizon > 0.0 ? predict(horizon, &st_pred) : Pose{state_->x, state_->y, state_->yaw};
      const Location ploc = horizon > 0.0 ? locate(p.x, p.y) : loc;
      const double ld = std::clamp(ld_base_ + ld_gain_ * std::fabs(v_actual_), ld_base_, 15.0);
      const Pt target = point_at(ploc.s + ld, ploc.index);
      const double alpha = wrap(std::atan2(target.y - p.y, target.x - p.x) - p.yaw);
      steer = std::clamp(std::atan2(2.0 * wheelbase_ * std::sin(alpha), ld), -max_steer_, max_steer_);
      if (mode_ == "stanley") {
        steer = steer_stanley(p, v_actual_);
      } else if (mode_ == "stanley_ff") {
        steer = steer_stanley_ff(p, v_actual_);
      } else if (mode_ == "lqr") {
        steer = steer_lqr(p, st_pred, v_actual_);
      } else if (blend_lqr_ > 0.0) {  // combination: pure pursuit (good straight/circle) + LQR (good wave)
        steer = std::clamp((1.0 - blend_lqr_) * steer + blend_lqr_ * steer_lqr(p, st_pred, v_actual_),
            -max_steer_, max_steer_);
      } else if (ff_gain_ > 0.0) {  // pure pursuit blended with curvature feed-forward
        const double ff = std::atan(wheelbase_ * kappa_at(ploc.s + std::fabs(v_actual_) * ff_time_, ploc.index));
        steer = std::clamp((1.0 - ff_gain_) * steer + ff_gain_ * ff, -max_steer_, max_steer_);
      }

      // --- speed: smallest of (cruise, curve limits, braking limit), looking ahead
      double v = cruise_;
      if (remaining <= 0.0) {
        v = 0.0;  // at the finish: stop
      } else {
        const size_t horizon =
          static_cast<size_t>((cruise_ * cruise_ / (2.0 * brake_) + 10.0) / 0.5) + 1;
        const size_t last = std::min(finish_, loc.index + horizon);
        for (size_t j = loc.index; j <= last; ++j) {
          const double dist = std::max(0.0, s_[j] - loc.s);
          const double vc = kappa_[j] > 1e-4 ? std::sqrt(a_lat_ / kappa_[j]) : cruise_;
          // can we still brake from here down to vc by node j?
          v = std::min(v, std::sqrt(vc * vc + 2.0 * brake_ * dist));
        }
        // and brake so that we stop about `stop_aim` past the finish line
        if (bang_) {
          // Time-optimal: keep full speed, then command 0 once the stopping distance at full decel reaches the
          // aim point. Commanding 0 saturates the speed loop at -6 m/s^2 at once; following a ramp does not.
          // The brake point is only checked once per control period; at full throttle the car gains ~1 m/s per
          // 0.05 s, so at 20 Hz the stop spread is ~5 m (offline: +0.2..+5.6 m). Use control_hz 100 with bang_brake.
          const double va = std::max(0.0, v_actual_);
          if (braking_ || remaining + stop_aim_ <= va * va / (2.0 * bang_decel_) + (bang_lead_ + period_) * va) {
            braking_ = true;
            v = 0.0;
          }
        } else {
          v = std::min(v, std::sqrt(2.0 * brake_ * (remaining + stop_aim_)));
        }
      }
      velocity = std::clamp(v, 0.0, cruise_);
      if (bang_ && braking_) {  // full braking: a large negative command keeps the speed loop saturated at -6 m/s^2
        velocity = v_actual_ > bang_release_ ? bang_neg_ : 0.0;
      }
      // After the finish the speed loop undershoots below 0 and the car rolls backward; the simulator only
      // calls it "stopped" after < 5 cm of movement in 1 s, so the roll costs up to 1 s. Push it back to 0.
      if (remaining <= 0.0 && stop_damp_ > 0.0 && v_actual_ < 0.0) {
        velocity = std::min(1.0, -stop_damp_ * v_actual_);
      }

      RCLCPP_INFO_THROTTLE(
        get_logger(), *get_clock(), 1000,
        "s=%.1f remaining=%.1f v_cmd=%.1f v_act=%.1f steer=%.2f", loc.s, remaining, velocity,
        v_actual_, steer);
    }

    // Always publish (20 Hz): the sim zeroes the car if commands stop for 0.5 s.
    VehCtrl msg;
    msg.header.stamp = now();
    msg.velocity = velocity;
    msg.steer = steer;
    last_steer_ = steer;  // the prediction needs the command the wheel is moving toward
    last_velocity_ = velocity;
    publisher_->publish(msg);
  }

  // ------------------------------------------------------------------ data
  std::vector<Pt> pts_;
  std::vector<double> s_, kappa_, kappa_s_;
  size_t finish_ = 0, progress_ = 0;
  std::optional<VehState> state_;
  double v_actual_ = 0.0, steer_actual_ = 0.0, last_steer_ = 0.0;
  double predict_, steer_tau_, steer_rate_, stop_damp_;
  std::string mode_;
  double st_k_, st_soft_, st_yaw_, st_dt_, st_decay_, ff_time_, ff_gain_;
  double lqr_qe_, lqr_qpsi_, lqr_r_, lqr_dt_, blend_lqr_, bang_decel_, bang_lead_, bang_neg_, bang_release_;
  bool bang_ = false, braking_ = false;
  double last_velocity_ = 0.0, period_ = 0.05, pi_int_ = 0.0, st_kp_, st_ki_;
  bool steer_pi_ = false;
  int st_n_;
  bool use_age_;

  double cruise_, a_lat_, brake_, stop_aim_, ld_base_, ld_gain_, wheelbase_, max_steer_;

  rclcpp::Subscription<RefPath>::SharedPtr path_sub_;
  rclcpp::Subscription<VehState>::SharedPtr state_sub_;
  rclcpp::Subscription<VehCtrl>::SharedPtr actual_sub_;
  rclcpp::Subscription<std_msgs::msg::Empty>::SharedPtr reset_sub_;
  rclcpp::Publisher<VehCtrl>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Driver>());
  rclcpp::shutdown();
  return 0;
}
