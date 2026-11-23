#!/usr/bin/env python3
"""2026-11-23 Full chain: cones -> FSGPathPlan -> our driver (plan A).

The simulator publishes the TRUE path on /path. This node turns it into cones (blue left, yellow right), but at every
planning step only gives FSGPathPlan the cones the car can SEE (within `range` m and +-fov/2 of the heading, like a
camera/lidar). FSGPathPlan predicts the centre line from the car's pose; we publish it on /planned_path at `rate` Hz.
The driver is started with `-r /path:=/planned_path`, so it never sees the true path. The scorer still uses the true path.

Finish: on a real track = orange cones. Here the finish becomes known when it is within `finish_range` m (default = cone
range), more than 2 m in front of the car and near the planned path (within 10 m; the circle's finish is AT the car at the start, so it is
not taken then). `min_travel` m only guards "passed the finish". Not known yet -> finish_index = last node (60 m ahead). Car crossed the finish (within
5 m, now behind) -> finish_index 0 (= stop now) until the next run.

Run (system python3, ROS sourced; FSGPathPlan needs only numpy):
  python3 cone_planner_node.py [--fsg DIR] [--range 15] [--fov 100] [--width 5] [--spacing 4] [--noise 0] [--rate 10]
"""
import argparse, math, sys, time
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline

ap = argparse.ArgumentParser()
ap.add_argument("--fsg", default=str(Path.home() / "Desktop/pleng/FSGPathPlan"))
ap.add_argument("--range", type=float, default=15.0, help="cone sensing range [m] (FSGPathPlan get_cones_in_fov: 15)")
ap.add_argument("--fov", type=float, default=100.0, help="field of view [deg] (FSGPathPlan default 100)")
ap.add_argument("--width", type=float, default=5.0, help="track width between blue and yellow [m]; MARGIN = width/2")
ap.add_argument("--spacing", type=float, default=4.0, help="cone spacing along the track [m]")
ap.add_argument("--noise", type=float, default=0.0, help="cone position noise per frame, std [m]")
ap.add_argument("--rate", type=float, default=10.0, help="re-plan rate [Hz]")
ap.add_argument("--steps", type=int, default=40, help="planner steps (x STEP_SIZE 1.5 m)")
ap.add_argument("--min_travel", type=float, default=20.0)
ap.add_argument("--finish_range", type=float, default=-1.0,
                help="finish (orange cones) known within this distance [m]; -1 = same as --range")
ap.add_argument("--ds", type=float, default=0.5, help="published node spacing [m] (driver expects 0.5)")
a, ros_args = ap.parse_known_args()
sys.path.insert(0, a.fsg)
import hyper as hyp                      # FSGPathPlan
hyp.MARGIN = a.width / 2.0               # the planner keeps MARGIN from each cone line = half the track width
hyp.NUM_STEPS = a.steps
import object as obj                     # FSGPathPlan
from Path_planer import PathPlanner      # FSGPathPlan

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from geometry_msgs.msg import Point
from std_msgs.msg import Empty
from thr_sim_msgs.msg import RefPath, VehState


class ConePlanner(Node):
    def __init__(self):
        super().__init__("cone_planner")
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
        self.pub = self.create_publisher(RefPath, "/planned_path", latched)
        self.create_subscription(RefPath, "/path", self.on_path, latched)
        self.create_subscription(VehState, "/veh_state", self.on_state, 10)
        self.create_subscription(Empty, "/reset", self.on_reset, 10)
        self.planner = PathPlanner()
        self.rng = np.random.default_rng()
        self.cones = None          # (N,2) positions
        self.colors = []
        self.finish = None
        self.state = None
        self.reset_run()
        self.create_timer(1.0 / a.rate, self.tick)
        self.n_plans, self.t_plan = 0, 0.0
        self.get_logger().info(f"cone planner: range {a.range} m, fov {a.fov} deg, width {a.width} m, "
                               f"spacing {a.spacing} m, noise {a.noise} m, {a.rate} Hz")

    def reset_run(self):
        self.state, self.last_xy, self.travel, self.passed = None, None, 0.0, False

    def on_reset(self, _):
        self.reset_run()

    def on_path(self, m):
        self.reset_run()
        if len(m.nodes) < 2:          # "no task": pass it on
            self.cones = None
            self.pub.publish(RefPath(header=m.header, nodes=[], finish_index=0))
            return
        pts = np.array([[p.x, p.y] for p in m.nodes])
        self.finish = pts[m.finish_index]
        seg = np.diff(pts, axis=0)
        s = np.concatenate([[0.0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
        cones, colors = [], []
        for sc in np.arange(0.0, s[-1], a.spacing):
            i = min(int(np.searchsorted(s, sc)), len(pts) - 2)
            h = math.atan2(pts[i + 1, 1] - pts[i, 1], pts[i + 1, 0] - pts[i, 0])
            nx, ny = -math.sin(h), math.cos(h)
            cones += [pts[i] + np.array([nx, ny]) * a.width / 2, pts[i] - np.array([nx, ny]) * a.width / 2]
            colors += [obj.BLUE, obj.YELLOW]
        self.cones, self.colors = np.array(cones), colors

    def on_state(self, m):
        if self.last_xy is not None:
            step = math.hypot(m.x - self.last_xy[0], m.y - self.last_xy[1])
            if step > 2.0:       # teleport back to the start (new run): not driven distance
                self.travel, self.passed = 0.0, False
            else:
                self.travel += step
        self.last_xy = (m.x, m.y)
        self.state = m

    def tick(self):
        if self.cones is None or self.state is None:
            return
        x, y, yaw = self.state.x, self.state.y, self.state.yaw
        d = self.cones - np.array([x, y])
        dist = np.hypot(d[:, 0], d[:, 1])
        bearing = np.arctan2(d[:, 1], d[:, 0]) - yaw
        bearing = np.arctan2(np.sin(bearing), np.cos(bearing))
        vis = (dist <= a.range) & (np.abs(bearing) <= math.radians(a.fov) / 2)
        seen = self.cones[vis] + (self.rng.normal(0.0, a.noise, (vis.sum(), 2)) if a.noise > 0 else 0.0)
        cones = [obj.Cone(float(c[0]), float(c[1]), col) for c, col in zip(seen, np.array(self.colors)[vis])]
        t0 = time.time()
        raw, _, _ = self.planner.generate_path((x, y), yaw, cones)
        self.t_plan += time.time() - t0
        self.n_plans += 1
        # smooth resample at ds with a cubic spline over arc length (the driver computes curvature from the nodes)
        line = np.vstack([[x, y], np.array(raw)])
        seg = np.diff(line, axis=0)
        s = np.concatenate([[0.0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
        cs = CubicSpline(s, line, bc_type="natural")
        nodes = cs(np.arange(0.0, s[-1], a.ds))
        # finish
        fin = len(nodes) - 1     # finish not known yet: the end of the plan
        f = self.finish
        fr = a.finish_range if a.finish_range > 0 else a.range
        dist_f = math.hypot(f[0] - x, f[1] - y)
        ahead = (f[0] - x) * math.cos(yaw) + (f[1] - y) * math.sin(yaw)
        if self.travel >= a.min_travel and dist_f < 5.0 and ahead < 0.0:
            self.passed = True   # crossed the finish: stays set until the next run
        if self.passed:
            fin = 0              # stop now
        elif dist_f <= fr and ahead > 2.0:   # in front (circle: at the start it is AT the car, so not taken)
            dn = np.hypot(nodes[:, 0] - f[0], nodes[:, 1] - f[1])
            if dn.min() < 3.0:   # the planned path reaches the finish: use that point
                fin = int(np.argmin(dn))
            else:                # plan does not reach it yet (beyond the seen cones it is only a straight guess, e.g. circle):
                # put the finish at the STRAIGHT-LINE distance; it is never longer than the real distance along the
                # track, so the car brakes a little early, never late
                fin = min(len(nodes) - 1, int(dist_f / a.ds))
        msg = RefPath()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.nodes = [Point(x=float(p[0]), y=float(p[1]), z=0.0) for p in nodes]
        msg.finish_index = fin
        self.pub.publish(msg)
        if self.n_plans % 100 == 0:
            self.get_logger().info(f"{self.n_plans} plans, mean {1000 * self.t_plan / self.n_plans:.1f} ms, "
                                   f"{len(cones)} cones seen, travel {self.travel:.1f} m, finish_index {fin}")


def main():
    rclpy.init(args=ros_args)
    node = ConePlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
