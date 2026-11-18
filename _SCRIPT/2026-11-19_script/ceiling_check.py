#!/usr/bin/env python3
"""Best possible time score on the straight, using the simulator's OWN vehicle model and sim.yaml values.

Full throttle (command 30 m/s), then full braking at a chosen point; searches the brake point that gives the highest
v_eq = 60 m / time-to-rest while stopping inside the 5 m free zone (55..65 m). No steering, no noise: a perfect driver.
Usage: python3 _SCRIPT/2026-11-19_script/ceiling_check.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "simulator", "thr_sim"))
from thr_sim.bicycle_model import BicycleModel

best = None
for i in range(100, 600):
    xb = i * 0.1
    m = BicycleModel(max_speed=30, max_accel=20, max_decel=6, speed_kp=8, speed_ki=9,
                     steer_kp=4, steer_ki=50, max_steer_rate=1.0)
    m.reset()
    t, braking, vmax = 0.0, False, 0.0
    while t < 20:
        braking = braking or m.state.x >= xb
        m.step(-30.0 if braking else 30.0, 0.0, 0.01)
        t += 0.01
        vmax = max(vmax, m.state.v)
        if braking and m.state.v < 0.02:
            break
    if 55 <= m.state.x <= 65 and (best is None or 60 / t > best[0]):
        best = (60 / t, xb, t, m.state.x, vmax)
v, xb, t, xs, vmax = best
print(f"perfect straight: brake at x={xb:.1f} m, peak {vmax:.1f} m/s, at rest after {t:.2f} s at x={xs:.1f} m")
print(f"v_eq = {v:.2f} m/s -> time score {40 * min(v, 30) / 30:.1f}/40  (40/40 needs v_eq 30 m/s, i.e. at rest after 2.0 s)")
