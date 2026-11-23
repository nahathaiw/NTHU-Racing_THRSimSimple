#!/usr/bin/env python3
"""2026-11-23 Try FSGPathPlan (github.com/weichang0307/FSGPathPlan, cloned to ~/Desktop/pleng/FSGPathPlan, not in this repo).

FSGPathPlan predicts the track centre line from CONES (blue = left, yellow = right): 40 steps of 1.5 m, each heading picked
by gradient ascent on prior (do not turn sharply) x likelihood (stay MARGIN from blue on the left and yellow on the right),
then a force smoother. Here we measure how close its predicted path is to the TRUE centre line.

  Part A: tracks from FSGPathPlan's own generator (random FSG-like loops), several seeds.
  Part B: our 4 THRSim paths turned into cones (width 5 m = 2 x MARGIN, one pair every 4 m).
Error = distance from each predicted point to the true centre line (only where the true line exists).

Run (needs numpy, scipy, matplotlib, pandas; the conda env dev_py has them):
  /home/sigma/anaconda3/envs/dev_py/bin/python _SCRIPT/2026-11-23_script/fsg_try.py [--fsg ~/Desktop/pleng/FSGPathPlan]
Output: _RESULTS/2026-11-23_eval-result/<date_time>_fsg_try/  (summary.txt, fsg_tracks.png, thrsim_paths.png)
"""
import argparse, math, sys, time
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--fsg", default=str(Path.home() / "Desktop/pleng/FSGPathPlan"))
ap.add_argument("--seeds", type=int, default=4)
ap.add_argument("--width", type=float, default=5.0, help="cone track width for Part B [m]")
ap.add_argument("--spacing", type=float, default=4.0, help="cone spacing for Part B [m]")
a = ap.parse_args()
sys.path.insert(0, a.fsg)
sys.path.insert(0, str(WS / "simulator/thr_sim"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import object as obj                       # FSGPathPlan
from Path_planer import PathPlanner        # FSGPathPlan
from Path_smoother import PathSmoother     # FSGPathPlan
from track_generate import FSTrackGenerator  # FSGPathPlan
from thr_sim.path_utils import make_path   # our simulator

OUT = WS / "_RESULTS/2026-11-23_eval-result" / f"{time.strftime('%Y-%m-%d_%H%M')}_fsg_try"
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "summary.txt", "w")


def say(s=""):
    print(s); log.write(s + "\n"); log.flush()


def dist_to_line(p, line):
    """distance from each point in p (N,2) to polyline `line` (M,2), by segment projection"""
    a0, a1 = line[:-1], line[1:]
    d = a1 - a0
    l2 = np.maximum((d ** 2).sum(1), 1e-12)
    out = []
    for q in p:
        t = np.clip(((q - a0) * d).sum(1) / l2, 0, 1)
        proj = a0 + t[:, None] * d
        out.append(np.sqrt(((proj - q) ** 2).sum(1)).min())
    return np.array(out)


def plan(start, yaw, cones):
    raw, probs, t_plan = PathPlanner().generate_path(tuple(start), yaw, cones)
    sm = PathSmoother()
    sm.load_data([tuple(start)] + list(raw), cones)
    smooth, t_smooth = sm.smooth_path()
    return np.array(raw), np.array(smooth[1:]), np.array(probs), t_plan, t_smooth


def report(name, true_line, raw, smooth, probs, t_plan, t_smooth):
    er, es = dist_to_line(raw, true_line), dist_to_line(smooth, true_line)
    say(f"{name:22s} raw: mean {er.mean():.2f} m, max {er.max():.2f} m | smoothed: mean {es.mean():.2f} m, "
        f"max {es.max():.2f} m | confidence at end {probs[-1]:.2g} | time {1000 * t_plan:.0f} + {1000 * t_smooth:.0f} ms")
    return er, es


# ------------------------------------------------------------------ Part A: FSG tracks
say(f"FSGPathPlan try, {time.strftime('%Y-%m-%d %H:%M')}  (planner: 40 steps x 1.5 m = 60 m ahead)")
say("\nPart A: FSGPathPlan's own random tracks (width 5 m, cones every 4 m, as in its test.ipynb)")
fig, axs = plt.subplots(1, a.seeds, figsize=(5 * a.seeds, 5))
for k in range(a.seeds):
    np.random.seed(k)
    g = FSTrackGenerator(track_width=5, cone_spacing=4, num_control_points=20, randomness=0.6, min_turn_radius=3)
    g.generate()
    cones = [obj.Cone(x, y, obj.BLUE) for x, y, _ in g.blue_cones] + \
            [obj.Cone(x, y, obj.YELLOW) for x, y, _ in g.yellow_cones]
    cl = np.array([[x, y] for x, y, _ in g.center_line])
    start, nxt = cl[0], cl[5]
    yaw = math.atan2(nxt[1] - start[1], nxt[0] - start[0])
    raw, smooth, probs, tp, ts = plan(start, yaw, cones)
    report(f"FSG track seed {k}", cl, raw, smooth, probs, tp, ts)
    ax = axs[k] if a.seeds > 1 else axs
    ax.plot(cl[:, 0], cl[:, 1], "k-", lw=0.8, label="true centre")
    ax.scatter([c.x for c in cones if c.color == obj.BLUE], [c.y for c in cones if c.color == obj.BLUE], s=8, c="tab:blue")
    ax.scatter([c.x for c in cones if c.color == obj.YELLOW], [c.y for c in cones if c.color == obj.YELLOW], s=8, c="gold")
    ax.plot(raw[:, 0], raw[:, 1], "r.-", ms=3, lw=1, label="planned (raw)")
    ax.plot(smooth[:, 0], smooth[:, 1], "g-", lw=1.5, label="planned + smoothed")
    ax.plot(*start, "ko", ms=6)
    ax.set_aspect("equal"); ax.set_title(f"FSG track seed {k}"); ax.grid(alpha=0.3)
axs[0].legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "fsg_tracks.png", dpi=110)

# ------------------------------------------------------------------ Part B: THRSim paths as cones
say(f"\nPart B: our THRSim paths as cones (width {a.width} m, one pair every {a.spacing} m)")
fig, axs = plt.subplots(2, 2, figsize=(14, 9))
for ax, shape in zip(axs.flat, ["straight", "wave", "lane_change", "circle"]):
    pts, fin = make_path(shape)
    seg = np.diff(pts, axis=0)
    s = np.concatenate([[0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
    cones = []
    for sc in np.arange(0, s[-1], a.spacing):
        i = min(np.searchsorted(s, sc), len(pts) - 2)
        h = math.atan2(*(pts[i + 1] - pts[i])[::-1])
        nx, ny = -math.sin(h), math.cos(h)   # left normal
        cones.append(obj.Cone(pts[i, 0] + nx * a.width / 2, pts[i, 1] + ny * a.width / 2, obj.BLUE))
        cones.append(obj.Cone(pts[i, 0] - nx * a.width / 2, pts[i, 1] - ny * a.width / 2, obj.YELLOW))
    yaw0 = math.atan2(pts[1, 1] - pts[0, 1], pts[1, 0] - pts[0, 0])
    raw, smooth, probs, tp, ts = plan(pts[0], yaw0, cones)
    er, es = report(f"THRSim {shape}", pts, raw, smooth, probs, tp, ts)
    ax.plot(pts[:, 0], pts[:, 1], "k-", lw=0.8, label="true path")
    ax.scatter([c.x for c in cones if c.color == obj.BLUE], [c.y for c in cones if c.color == obj.BLUE], s=8, c="tab:blue")
    ax.scatter([c.x for c in cones if c.color == obj.YELLOW], [c.y for c in cones if c.color == obj.YELLOW], s=8, c="gold")
    ax.plot(raw[:, 0], raw[:, 1], "r.-", ms=3, lw=1, label=f"planned raw (mean err {er.mean():.2f} m)")
    ax.plot(smooth[:, 0], smooth[:, 1], "g-", lw=1.5, label=f"smoothed (mean err {es.mean():.2f} m)")
    ax.set_aspect("equal"); ax.set_title(f"THRSim {shape}"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "thrsim_paths.png", dpi=110)
say(f"\nplots: {OUT}/fsg_tracks.png, {OUT}/thrsim_paths.png")
