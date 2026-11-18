#!/usr/bin/env python3
"""Draw the pure-pursuit geometry used by my_driver.

Left:  car, path, carrot point, lookahead ld, angle alpha, steering delta.
Right: the same 1 m error with two lookaheads (ld = 8.75 m and 6.25 m, i.e. gain 0.25 and 0.15 at 25 m/s).

Usage: python3 _SCRIPT/2026-11-18_script/plot_pure_pursuit.py [output.png]      (default _LOG/2026-11-18_log-and-diagram/diagrams/2026-11-18_2125_pure-pursuit-geometry.png)
All angles are computed with the same formula as driver_node.cpp:
    steer = atan(2 * L * sin(alpha) / ld)
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Rectangle

plt.rcParams["font.family"] = "DejaVu Sans Mono"   # so that "ld" is not mistaken for "Id"
L = 2.5                      # wheelbase [m]
INK, PAPER = "#12202F", "#F4F1E9"
TEAL, ORANGE, MUTED = "#0F766E", "#C2410C", "#4A5568"


def steering(alpha, ld):
    return np.arctan2(2.0 * L * np.sin(alpha), ld)


def arc_points(alpha, ld, n=60):
    """Circle through the rear axle, tangent to the heading (+x), that reaches the carrot."""
    r = ld / (2.0 * np.sin(alpha))
    th = np.linspace(0.0, 2.0 * alpha, n)
    return r * np.sin(th), r * (1.0 - np.cos(th))


out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "_LOG", "2026-11-18_log-and-diagram", "diagrams", "2026-11-18_2125_pure-pursuit-geometry.png")
os.makedirs(os.path.dirname(out), exist_ok=True)

fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1.25, 1]})
fig.patch.set_facecolor(PAPER)
for a in (ax, bx):
    a.set_facecolor(PAPER)
    for s in a.spines.values():
        s.set_visible(False)
    a.set_xticks([])
    a.set_yticks([])

# ------------------------------------------------------------------ left: geometry
ld = 8.0
px = np.linspace(-3, 15, 300)
py = 2.2 + 0.02 * px ** 2                     # a path that curves away to the left
i = np.argmin(np.abs(np.hypot(px, py) - ld))  # carrot: point on the path ld away from the rear axle
cx, cy = px[i], py[i]
alpha = np.arctan2(cy, cx)
delta = steering(alpha, ld)

ax.plot(px, py, "--", color=INK, lw=2.5)
ax.text(11.0, 6.2, "path", color=INK, fontsize=15, weight="bold")

# car body, rear axle at the origin, front axle at x = L
ax.add_patch(Rectangle((-0.6, -0.8), 3.6, 1.6, fc="#D9D3C3", ec=INK, lw=1.5, zorder=2))
ax.plot([0], [0], "o", color=INK, ms=7, zorder=5)
ax.plot([L], [0], "o", color=INK, ms=7, zorder=5)
w = 0.9                                          # front wheel, turned by delta
ax.plot([L - w * np.cos(delta), L + w * np.cos(delta)], [-w * np.sin(delta), w * np.sin(delta)],
        color=INK, lw=7, solid_capstyle="round", zorder=4)
ax.text(-1.2, -1.9, "rear axle", color=MUTED, fontsize=11)
ax.text(2.3, -2.5, "front axle", color=MUTED, fontsize=11)
ax.text(0.4, 1.05, "car", color=INK, fontsize=14, weight="bold")

ax.plot([0, ld + 1.2], [0, 0], ":", color=MUTED, lw=2)           # car heading
ax.text(ld + 1.3, -0.35, "heading", color=MUTED, fontsize=13)

ax.plot([0, cx], [0, cy], "-", color=ORANGE, lw=3, zorder=3)     # lookahead
ax.text(cx * 0.45 - 0.9, cy * 0.45 + 0.35, "ld", color=ORANGE, fontsize=20, weight="bold")

ax.plot([cx], [cy], "o", color=ORANGE, ms=15, zorder=6)          # the carrot
ax.text(cx + 0.5, cy + 0.4, "carrot\n(target point)", color=ORANGE, fontsize=14, weight="bold")

ax.add_patch(Arc((0, 0), 6.0, 6.0, theta1=0, theta2=np.degrees(alpha), color=TEAL, lw=3))
ax.text(3.6, 0.9, "α", color=TEAL, fontsize=22, weight="bold")

ex, ey = arc_points(alpha, ld)                                   # path the car will drive
ax.plot(ex, ey, color=TEAL, lw=2.5, alpha=0.9, zorder=1)
ax.text(2.2, -3.0, "δ = steering angle of the front wheel", color=TEAL, fontsize=14, weight="bold")
ax.annotate("δ", xy=(L + 0.5, 0.05), xytext=(L + 1.0, -1.25), color=TEAL, fontsize=22, weight="bold",
            arrowprops=dict(arrowstyle="-", color=TEAL, lw=1.5))

ax.set_xlim(-2.5, 17)
ax.set_ylim(-4.2, 9.0)
ax.set_aspect("equal")
ax.set_title("Pure pursuit: aim at a point ld ahead on the path", color=INK, fontsize=15, weight="bold", loc="left")
ax.text(-2.3, 8.0, "δ = atan( 2 · L · sin α  /  ld )      L = 2.5 m", color=INK, fontsize=14,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=INK))
ax.text(-2.3, 6.8, f"here: α = {np.degrees(alpha):.0f}°,  ld = {ld:.0f} m  →  δ = {np.degrees(delta):.0f}°", color=MUTED, fontsize=14)

# ------------------------------------------------------------------ right: short vs long lookahead
e = 1.0                                           # car is 1 m to the side of a straight path
bx.plot([-0.5, 12], [e, e], "--", color=INK, lw=2.5)
bx.text(8.8, e + 0.12, "path", color=INK, fontsize=14, weight="bold")
bx.add_patch(Rectangle((-0.6, -0.15), 1.2, 0.3, fc="#D9D3C3", ec=INK, lw=1.2, zorder=3))
bx.plot([0], [0], "o", color=INK, ms=6, zorder=5)

rows = [(8.75, TEAL, "long lookahead\nld = 8.75 m  (gain 0.25 at 25 m/s)", 0.62),
        (6.25, ORANGE, "short lookahead\nld = 6.25 m  (gain 0.15: set I)", 0.28)]
vals = []
for ldv, col, label, ytxt in rows:
    x = np.sqrt(ldv ** 2 - e ** 2)
    al = np.arctan2(e, x)
    de = steering(al, ldv)
    vals.append(de)
    px_, py_ = arc_points(al, ldv)
    bx.plot(px_, py_, color=col, lw=3)
    bx.plot([x], [e], "o", color=col, ms=11, zorder=6)
    bx.text(0.2, -0.45 - (0.95 if col == ORANGE else 0.0), f"{label}\n→ δ = {np.degrees(de):.1f}°",
            color=col, fontsize=14, weight="bold", va="top")

bx.set_xlim(-0.8, 12)
bx.set_ylim(-2.7, 1.9)
bx.set_title("Same 1 m error, different lookahead", color=INK, fontsize=15, weight="bold", loc="left")
bx.text(-0.6, 1.62, f"The short lookahead steers {vals[1] / vals[0]:.1f}× harder", color=ORANGE, fontsize=16, weight="bold")
bx.text(-0.6, 1.38, "for the same error, so it over-corrects and wiggles", color=MUTED, fontsize=13)
bx.text(11.9, -2.6, "(vertical scale exaggerated)", color=MUTED, fontsize=11, ha="right")

fig.tight_layout()
fig.savefig(out, dpi=150, facecolor=PAPER)
print("saved", os.path.abspath(out), f"| left: alpha={np.degrees(alpha):.1f} deg, delta={np.degrees(delta):.1f} deg",
      f"| right: {np.degrees(vals[0]):.2f} deg vs {np.degrees(vals[1]):.2f} deg, ratio {vals[1] / vals[0]:.2f}")
