#!/usr/bin/env python3
"""Keep the 2025-2026 citing papers that are about OUR problem (vehicle path tracking / racing control) and group them by method.

Reads _paper/citing_2025_2026/all_citing.json, writes relevant.json and a ranked shortlist per category to stdout.
Relevance = topic words in title/abstract + how many of our seed papers it cites + citations (new papers have few).
"""
import json, os, re

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_paper", "citing_2025_2026")
data = json.load(open(os.path.join(D, "all_citing.json")))

TOPIC = r"path.?tracking|trajectory.?tracking|path.?following|lateral control|steering control|pure.?pursuit|stanley|autonomous racing|race car|racecar|racing|f1tenth|formula student|lookahead|look-ahead"
OFF = r"\buav|drone|quadrotor|aerial|underwater|marine|vessel|ship|humanoid|legged|manipulator|robot arm|pedestrian prediction|traffic flow|lidar odometry|slam\b|object detection|segmentation"
CATS = [
    ("Delay / latency compensation", r"delay|latency|time.?lag|dead.?time|actuator dynamic|smith predictor"),
    ("Learning-based control (RL, GP, NN, residual)", r"reinforcement|gaussian process|neural|learning-based|learned|residual|koopman|imitation|data.?driven"),
    ("MPC / optimisation-based tracking", r"model predictive|\bmpc\b|nmpc|optimal control|optimi[sz]ation-based|mpcc"),
    ("Improved pure pursuit / geometric", r"pure.?pursuit|lookahead|look-ahead|geometric|stanley"),
    ("Speed profile / minimum time / racing line", r"speed profile|velocity profile|minimum.?time|racing line|raceline|time.?optimal"),
]

rel = []
for wid, w in data["works"].items():
    w["title"] = w["title"] or ""
    text = (w["title"] + " " + (w["abstract"] or "")).lower()
    if not re.search(TOPIC, text) or re.search(OFF, w["title"].lower()):
        continue
    score = len(re.findall(TOPIC, text)) + 2 * len(w["cites"]) + min(w["cited_by"], 20) / 4
    cats = [c for c, rx in CATS if re.search(rx, text)] or ["Other"]
    rel.append(dict(w, id=wid, score=round(score, 1), cats=cats))
rel.sort(key=lambda r: -r["score"])
json.dump(rel, open(os.path.join(D, "relevant.json"), "w"), indent=1)
print(f"{len(rel)} relevant of {len(data['works'])}")
for c, _ in CATS + [("Other", "")]:
    group = [r for r in rel if c in r["cats"]]
    print(f"\n### {c}  ({len(group)})")
    for r in group[:12]:
        oa = "OA" if r["oa_pdf"] or r["is_oa"] else "--"
        print(f"  {r['score']:5.1f} {r['year']} {oa} cit{r['cited_by']:3d} [{','.join(r['cites'])}] {r['title'][:110]}")
