#!/usr/bin/env python3
"""C8 helper: does the car get better run after run? Prints RMS sideways error and score per path per run number,
for every config folder of a sweep (learning-from-past-runs check). Also writes learning_curve.png in the sweep folder.

Usage: ./_SCRIPT/2026-11-19_script/learning_curve.py _RESULTS/2026-11-19_eval-result/<date>_c8_ilc_learn
"""
import json, sys
from pathlib import Path

sweep = Path(sys.argv[1])
rows = {}
for d in sorted(p for p in sweep.iterdir() if (p / "eval.json").exists()):
    cid = d.name.split("_", 2)[-1]
    runs = json.load(open(d / "eval.json"))["runs"]
    per = {}
    for r in runs:
        per.setdefault(r["shape"], []).append(r)
    rows[cid] = per
    print(f"[{cid}]  rms sideways error [cm] per run (score in brackets)")
    for shape, rs in per.items():
        print(f"   {shape:12s} " + "  ".join(f"{100 * r['rms_cte']:5.1f} ({r['score']:.1f})" for r in rs))
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    shapes = ["straight", "wave", "lane_change", "circle"]
    fig, ax = plt.subplots(1, 4, figsize=(16, 3.6), sharey=False)
    for cid, per in rows.items():
        for a, s in zip(ax, shapes):
            if s in per:
                a.plot(range(1, len(per[s]) + 1), [100 * r["rms_cte"] for r in per[s]], marker="o", label=cid)
    for a, s in zip(ax, shapes):
        a.set_title(s); a.set_xlabel("run number"); a.grid(alpha=0.3)
    ax[0].set_ylabel("RMS sideways error [cm]"); ax[-1].legend(fontsize=8)
    fig.suptitle(f"Learning curve: {sweep.name}")
    fig.tight_layout(); fig.savefig(sweep / "learning_curve.png", dpi=110)
    print(f"plot: {sweep / 'learning_curve.png'}")
except ImportError:
    pass
