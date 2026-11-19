#!/usr/bin/env python3
"""C9: tune the adaptive-lookahead policy with policy search (cross-entropy method, CEM).

Idea from RA-L 2026 (RL-tuned pure-pursuit lookahead): the lookahead should depend on the situation.
Our policy:  ld = (lookahead_base + lookahead_gain * v) / (1 + ld_kappa * |kappa ahead|) - ld_err * |e|
CEM is the simplest RL policy-search method: sample a population of parameter sets around a mean, run each on the
REAL simulator (sweep.bash), keep the best few ("elite"), move the mean/spread toward them, repeat.
Each generation also runs B6 as a same-session reference (noise between sweeps is ~0.3-0.6).

Usage: ./_SCRIPT/2026-11-19_script/policy_search.py [--gens 4] [--pop 6] [--elite 3] [--runs 2]
Output: one sweep folder per generation (c9_cem_gen<k>) + _RESULTS/2026-11-19_eval-result/<date>_c9_cem_log.json
"""
import argparse, json, random, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent.parent
RES = WS / "_RESULTS" / "2026-11-19_eval-result"
B6 = ("lat_accel:=40.0 cruise_speed:=30.0 stop_aim:=1.5 lookahead_gain:=0.09 predict_time:=0.10 blend_lqr:=0.3 "
      "lqr_r:=3.0 ff_time:=0.10 stop_damp:=5.0 bang_brake:=true control_hz:=100.0")
# name: (start mean, start spread, low, high)
SPACE = {"ld_kappa": (5.0, 5.0, 0.0, 25.0), "ld_err": (1.0, 1.0, 0.0, 5.0),
         "lookahead_gain": (0.09, 0.03, 0.03, 0.20), "lookahead_base": (2.5, 0.6, 1.5, 4.0)}


def run_generation(k, pop, runs):
    cfg = HERE / "configs" / f"c9_cem_gen{k}.txt"
    lines = [f"# C9 CEM generation {k}: adaptive lookahead policy, base = B6", f"B6REF {B6}"]
    for i, p in enumerate(pop):
        lines.append(f"G{k}P{i} {B6} " + " ".join(f"{n}:={v:.4f}" for n, v in p.items()))
    cfg.write_text("\n".join(lines) + "\n")
    subprocess.run([str(HERE / "sweep.bash"), f"c9_cem_gen{k}", str(cfg), "-n", str(runs)], check=False)
    out = sorted(RES.glob(f"*_c9_cem_gen{k}"))[-1] / "summary.txt"
    scores, cur = {}, None
    for line in out.read_text().splitlines():
        if m := re.match(r"\[(\S+)\]", line):
            cur = m.group(1)
        elif cur and (m := re.search(r"OVERALL ([\d.]+)", line)):
            scores[cur] = float(m.group(1))
    return scores, str(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=4)
    ap.add_argument("--pop", type=int, default=6)
    ap.add_argument("--elite", type=int, default=3)
    ap.add_argument("--runs", type=int, default=2)
    a = ap.parse_args()
    rng = random.Random(1119)
    mean = {n: s[0] for n, s in SPACE.items()}
    sd = {n: s[1] for n, s in SPACE.items()}
    log = {"started": time.strftime("%Y-%m-%d %H:%M"), "space": SPACE, "gens": []}
    logf = RES / f"{time.strftime('%Y-%m-%d_%H%M')}_c9_cem_log.json"
    best = (-1.0, None)
    for k in range(a.gens):
        pop = [{n: min(SPACE[n][3], max(SPACE[n][2], rng.gauss(mean[n], sd[n]))) for n in SPACE}
               for _ in range(a.pop)]
        if k == 0:
            pop[0] = dict(mean)   # always try the start point once
        scores, where = run_generation(k, pop, a.runs)
        ranked = sorted(((scores.get(f"G{k}P{i}", 0.0), p) for i, p in enumerate(pop)), key=lambda t: -t[0])
        elite = [p for _, p in ranked[:a.elite]]
        for n in SPACE:   # move toward the elite; keep a minimum spread so the search does not collapse on noise
            vals = [p[n] for p in elite]
            mean[n] = sum(vals) / len(vals)
            spread = (sum((v - mean[n]) ** 2 for v in vals) / len(vals)) ** 0.5
            sd[n] = max(0.5 * sd[n] + 0.5 * spread, 0.1 * SPACE[n][1])
        if ranked[0][0] > best[0]:
            best = ranked[0]
        log["gens"].append({"gen": k, "summary": where, "b6_ref": scores.get("B6REF"),
                            "results": [{"score": s, **p} for s, p in ranked], "new_mean": dict(mean), "new_sd": dict(sd)})
        log["best"] = {"score": best[0], **best[1]}
        logf.write_text(json.dumps(log, indent=1))
        print(f"== gen {k}: B6 ref {scores.get('B6REF')}, best {ranked[0][0]} {ranked[0][1]}", flush=True)
    print(f"done. best {best}. log: {logf}")


if __name__ == "__main__":
    sys.exit(main())
