#!/usr/bin/env python3
"""Offline test of the end-of-run creep, with the simulator's own speed PI loop (no noise).

The car brakes along the driver's profile, then the driver commands 0. The speed loop's integral makes the actual
speed undershoot below 0, the car rolls backward, and the simulator only calls it "stopped" after it moved < 5 cm
for 1 s. Compares stop strategies by the run time the simulator would record.
Usage: python3 _SCRIPT/2026-11-19_script/stop_creep_test.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "simulator", "thr_sim"))
from thr_sim.bicycle_model import PIActuator

L, BRAKE, AIM, CRUISE = 60.0, 5.9, 2.0, 25.0


def run(strategy, k=0.0):
    pi = PIActuator(8.0, 9.0, 20.0, 6.0, 30.0)
    x, t, cmd, hist = 0.0, 0.0, 0.0, []
    for step in range(3000):                          # 100 Hz, 30 s
        if step % 5 == 0:                             # driver at 20 Hz
            rem = L - x
            if rem > 0:
                cmd = min(CRUISE, (2 * BRAKE * (rem + AIM)) ** 0.5)
            else:
                cmd = 0.0 if strategy == "zero" else max(0.0, -k * pi.value)
        v = pi.step(cmd, 0.01)
        x += v * 0.01
        t += 0.01
        hist.append((t, x))
        w = [p for p in hist if p[0] > t - 1.0 - 1e-9]  # simulator's rest rule
        if t > 2 and w[0][0] <= t - 1.0 + 0.011 and all(abs(x - px) < 0.05 for _, px in w):
            return w[0][0], x, min(v for v in [pi.value])
    return None, x, None


for name, k in [("zero", 0), ("cancel k=1", 1), ("cancel k=2", 2), ("cancel k=4", 4), ("cancel k=8", 8)]:
    t, x, _ = run("zero" if k == 0 else "cancel", k)
    print(f"{name:12s} at rest after {t:.2f} s, stopped at {x:.2f} m (v_eq {L / t:.2f})")
