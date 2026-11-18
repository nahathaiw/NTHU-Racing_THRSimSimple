#!/usr/bin/env python3
"""Record every run and plot commanded vs actual (hint: "draw the data and observe it").

Listens to /path, /reset, /veh_ctrl (command), /veh_actual (what the car really does),
/veh_state (pose) and /sim_status (run result). For each run it writes, into OUT_DIR:
    <NN>_<shape>.csv   one row per /veh_state message (50 Hz)
    <NN>_<shape>.png   4 plots: speed, steering, cross-track error, top view
and prints the measured delay between command and actual (steering and speed).

Usage (ROS and the workspace sourced, system python):
    python3 record_run.py OUT_DIR            # stops with Ctrl+C
"""
import csv
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Empty, String
from thr_sim_msgs.msg import RefPath, VehCtrl, VehState

COLS = ["t", "x", "y", "yaw", "cmd_v", "cmd_steer", "act_v", "act_steer", "cte", "s"]


def delay(t, cmd, act, max_lag=0.6):
    """Lag (s) that best lines up act(t) with cmd(t - lag): least squared error."""
    t, cmd, act = map(np.asarray, (t, cmd, act))
    if len(t) < 20 or np.ptp(cmd) < 1e-6:
        return float("nan")
    best, best_err = 0.0, float("inf")
    for lag in np.arange(0.0, max_lag + 1e-9, 0.01):
        shifted = np.interp(t - lag, t, cmd)
        err = np.mean((act - shifted) ** 2)
        if err < best_err:
            best, best_err = lag, err
    return best


class Recorder(Node):
    def __init__(self, out):
        super().__init__("run_recorder")
        self.out, self.n = out, 0
        os.makedirs(out, exist_ok=True)
        latched = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(RefPath, "/path", self.on_path, latched)
        self.create_subscription(Empty, "/reset", self.on_reset, 10)
        self.create_subscription(VehCtrl, "/veh_ctrl", self.on_cmd, 10)
        self.create_subscription(VehCtrl, "/veh_actual", self.on_act, 10)
        self.create_subscription(VehState, "/veh_state", self.on_state, 10)
        self.create_subscription(String, "/sim_status", self.on_status, 10)
        self.path, self.rows, self.t0 = None, [], None
        self.cmd, self.act = (0.0, 0.0), (0.0, 0.0)
        self.get_logger().info(f"recording into {out}")

    def on_path(self, m):
        pts = np.array([[p.x, p.y] for p in m.nodes])
        self.path = pts if len(pts) > 1 else None
        if self.path is not None:
            seg = np.diff(self.path, axis=0)
            self.s_nodes = np.concatenate([[0.0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
            self.finish = m.finish_index
            self.progress = 0

    def on_reset(self, _m):
        self.rows, self.t0 = [], None
        self.progress = 0

    def on_cmd(self, m):
        self.cmd = (m.velocity, m.steer)

    def on_act(self, m):
        self.act = (m.velocity, m.steer)

    def project(self, x, y):
        """Signed cross-track error and distance along the path, searching forward only."""
        p = self.path
        hi = min(len(p) - 1, self.progress + 80)
        best = (float("inf"), 0.0, 0.0, self.progress)
        for i in range(self.progress, hi):
            a, b = p[i], p[i + 1]
            d = b - a
            L2 = d @ d
            u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - a[0]) * d[0] + (y - a[1]) * d[1]) / L2))
            q = a + u * d
            dist = math.hypot(x - q[0], y - q[1])
            if dist < best[0]:
                side = math.copysign(1.0, d[0] * (y - a[1]) - d[1] * (x - a[0]))
                best = (dist, side * dist, self.s_nodes[i] + u * math.sqrt(L2), i)
        self.progress = best[3]
        return best[1], best[2]

    def on_state(self, m):
        if self.path is None:
            return
        t = self.get_clock().now().nanoseconds * 1e-9
        if self.t0 is None:
            self.t0 = t
        cte, s = self.project(m.x, m.y)
        self.rows.append([t - self.t0, m.x, m.y, m.yaw, *self.cmd, *self.act, cte, s])

    def on_status(self, m):
        res = json.loads(m.data)
        if not self.rows:
            return
        self.n += 1
        name = f"{self.n:02d}_{res.get('shape', 'run')}"
        with open(os.path.join(self.out, name + ".csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(COLS)
            w.writerows(self.rows)
        self.plot(name, np.array(self.rows), res)
        self.rows, self.t0 = [], None

    def plot(self, name, d, res):
        t = d[:, 0]
        lag_st = delay(t, d[:, 5], d[:, 7])
        lag_v = delay(t, d[:, 4], d[:, 6])
        fig, ax = plt.subplots(2, 2, figsize=(14, 8))
        a = ax[0, 0]
        a.plot(t, d[:, 4], "--", label="command")
        a.plot(t, d[:, 6], label="actual")
        a.set(title=f"Speed (actual lags about {lag_v:.2f} s)", xlabel="time [s]", ylabel="m/s")
        a.legend()
        a = ax[0, 1]
        a.plot(t, np.degrees(d[:, 5]), "--", label="command")
        a.plot(t, np.degrees(d[:, 7]), label="actual")
        a.set(title=f"Steering (actual lags about {lag_st:.2f} s)", xlabel="time [s]", ylabel="deg")
        a.legend()
        a = ax[1, 0]
        a.plot(t, d[:, 8])
        a.axhline(0, color="k", lw=0.5)
        a.set(title=f"Cross-track error (RMS {np.sqrt(np.mean(d[:, 8] ** 2)):.2f} m, max {np.max(np.abs(d[:, 8])):.2f} m)",
              xlabel="time [s]", ylabel="m")
        a = ax[1, 1]
        a.plot(self.path[:, 0], self.path[:, 1], "k--", lw=1, label="path")
        a.plot(d[:, 1], d[:, 2], label="car")
        f = self.path[self.finish]
        a.plot(f[0], f[1], "rx", ms=10, label="finish")
        a.set(title="Top view", xlabel="x [m]", ylabel="y [m]")
        a.set_aspect("equal", adjustable="datalim")
        a.legend()
        fig.suptitle(f"{name}: {res.get('result')}  score {res.get('score')}  "
                     f"(track {res.get('tracking')}, time {res.get('time_score')}, stop {res.get('stop')}, "
                     f"v_eq {res.get('v_eq')} m/s)")
        fig.tight_layout()
        fig.savefig(os.path.join(self.out, name + ".png"), dpi=110)
        plt.close(fig)
        msg = f"{name}: steering delay {lag_st:.2f} s, speed delay {lag_v:.2f} s, score {res.get('score')}"
        self.get_logger().info(msg)
        with open(os.path.join(self.out, "delays.txt"), "a") as fh:
            fh.write(msg + "\n")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "observe"
    rclpy.init()
    node = Recorder(out)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
