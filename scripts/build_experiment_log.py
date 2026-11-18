#!/usr/bin/env python3
"""Build experiment_log/ from eval_results/ (which is gitignored).

One folder per experiment, named  YYYY-MM-DD_HHMM_<id>_<what-it-tested>  (HHMM = when the run finished, Taiwan time),
holding README.md (parameters + results), result.json, report.png and the driver/sim logs.
Also writes experiment_log/README.md (index + timeline).  Re-run any time:  python3 scripts/build_experiment_log.py
"""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "eval_results", ROOT / "experiment_log" / "experiments"
DEF = dict(cruise=12.0, lat=3.0, brake=3.5, aim=1.5, gain=0.40, base=2.5)

def P(**kw): d = dict(DEF); d.update(kw); return d
FIN = dict(cruise=25.0, lat=6.0, brake=5.9, aim=2.0, gain=0.25, base=2.5)

# (source json, slug, sweep, params, purpose, observation, extra)
E = [
 (None, "baseline_python-demo-driver", "baseline", None,
  "Measure the Python demo driver (3 m/s) on all four paths, 1 run each, in the GUI.",
  "Tracking 37-40/40 and stop 20/20 already; time only ~4/40. All the opportunity is speed. Score 62.3.", "baseline"),
 ("eval_20261118_195322", "first-run_defaults", "first run", P(),
  "First evaluation of my C++ driver with its default parameters (-n 3).",
  "Worked first time: 12/12 stopped, none off-track. Time points doubled (4 -> 8.7). Score 66.6.", ""),
 ("eval_20261118_195854", "repeat-defaults_noise-check", "first run", P(),
  "Same settings again to see run-to-run noise.", "66.3 vs 66.6: noise is roughly 0.3-0.5 points.", ""),
 ("sweep/B", "B_all-faster-small-step", "sweep 1", P(cruise=16.0, lat=4.0, brake=4.5, aim=2.5),
  "Raise speed limits a little.", "66.7. Barely better than the defaults.", ""),
 ("sweep/C", "C_all-faster-medium-step", "sweep 1", P(cruise=20.0, lat=5.0, brake=5.0, aim=3.0),
  "Next step up.", "67.0.", ""),
 ("sweep/D", "D_cruise25-lat6-brake5.5", "sweep 1", P(cruise=25.0, lat=6.0, brake=5.5, aim=3.5),
  "Big step: cruise 25, brake 5.5.", "68.5. Braking harder was the main gain.", ""),
 ("sweep/E", "E_cruise30-lat7_too-aggressive", "sweep 1", P(cruise=30.0, lat=7.0, brake=5.5, aim=3.5),
  "Even faster in curves.", "67.7. Tracking error grew (max 0.92 m); more speed stopped paying off.", ""),
 ("sweep/F", "F_lat8-cruise20", "sweep 1", P(cruise=20.0, lat=8.0, brake=5.0, aim=3.0),
  "Test a high lateral acceleration limit.", "68.0. Fine on the circle (69.6) but not better overall.", ""),
 ("sweep/G", "G_D-plus-gain0.25", "sweep 1", P(cruise=25.0, lat=6.0, brake=5.5, aim=3.5, gain=0.25),
  "D with a shorter lookahead gain (0.40 -> 0.25).", "68.8, best of sweep 1. Better wave tracking.", ""),
 ("sweep2/H", "H_G-with-aim3.0", "sweep 2", P(cruise=25.0, lat=6.0, brake=5.5, aim=3.0, gain=0.25),
  "G with a safer stop margin (aim 3.0).", "68.9.", ""),
 ("sweep2/I", "I_gain0.15_FAILED", "sweep 2", P(cruise=25.0, lat=6.0, brake=5.5, aim=3.0, gain=0.15),
  "Is an even shorter lookahead better?", "47.0: 3 runs left the track. A short lookahead steers about 2x harder for the same error (see experiment_log/diagrams/2026-11-18_2125_pure-pursuit-geometry.png).", ""),
 ("sweep2/J", "J_lat7", "sweep 2", P(cruise=25.0, lat=7.0, brake=5.5, aim=3.0, gain=0.25),
  "More lateral acceleration on top of H.", "68.7. No gain.", ""),
 ("sweep2/K", "K_brake5.8", "sweep 2", P(cruise=25.0, lat=6.0, brake=5.8, aim=3.0, gain=0.25),
  "Brake closer to the 6 m/s^2 limit.", "69.8 (partly luck: K2 repeat was 69.5). Time points up.", ""),
 ("sweep2/L", "L_base2.0_worse", "sweep 2", P(cruise=25.0, lat=6.0, brake=5.5, aim=3.0, gain=0.25, base=2.0),
  "Shorter lookahead at standstill.", "67.7: worse tracking (max 1.06 m). Keep base 2.5.", ""),
 ("sweep2/H2", "H2_repeat-of-H", "sweep 2", P(cruise=25.0, lat=6.0, brake=5.5, aim=3.0, gain=0.25),
  "Repeat of H to measure noise.", "69.4 vs 68.9: noise about 0.5.", ""),
 ("sweep3/K2", "K2_repeat-of-K", "sweep 3", P(cruise=25.0, lat=6.0, brake=5.8, aim=3.0, gain=0.25),
  "Repeat of K.", "69.5: K's 69.8 was partly noise.", ""),
 ("sweep3/M", "M_brake5.8-aim2.5", "sweep 3", P(cruise=25.0, lat=6.0, brake=5.8, aim=2.5, gain=0.25),
  "K with a smaller stop_aim (3.0 -> 2.5).", "69.4. Safer stop, same speed.", ""),
 ("sweep4/N", "N_brake5.9-aim2.0_BEST", "sweep 4", FIN,
  "Brake 5.9 (just under the car's 6.0 limit) and aim 2.0 to keep the stop inside 5 m.", "70.3, the best. Straight average speed 10.1 -> 11.6 m/s. Final settings.", ""),
 ("sweep4/O", "O_M-plus-gain0.30", "sweep 4", P(cruise=25.0, lat=6.0, brake=5.8, aim=2.5, gain=0.30),
  "Longer lookahead at speed.", "70.1. Tied with N within noise.", ""),
 ("sweep4/P", "P_M-plus-cruise30", "sweep 4", P(cruise=30.0, lat=6.0, brake=5.8, aim=2.5, gain=0.25),
  "Higher cruise ceiling.", "70.1. Tied with N within noise.", ""),
 ("eval_20261118_204311", "confirm-run-1_final-settings-N", "confirmation", FIN,
  "Confirmation run with the final settings (1 run per path).", "70.85 (single runs, so noisier).", "assumed"),
 ("eval_20261118_210332", "confirm-run-2_final-settings-N", "confirmation", FIN,
  "Second confirmation / demo run.", "70.43.", "assumed"),
 ("eval_20261118_213216", "confirm-run-3_final-settings-N", "confirmation", FIN,
  "Third confirmation / demo run.", "70.15.", "assumed"),
]

NAMES = dict(cruise="cruise_speed", lat="lat_accel", brake="brake_decel", aim="stop_aim", gain="lookahead_gain", base="lookahead_base")

def ptable(p):
    rows = "| Parameter | Value | Default |\n|---|---:|---:|\n"
    for k, n in NAMES.items():
        mark = "" if p[k] == DEF[k] else " **(changed)**"
        rows += f"| `{n}` | {p[k]}{mark} | {DEF[k]} |\n"
    return rows

def fmt(x, n=1):
    return "-" if x is None else f"{x:.{n}f}"

def results(d):
    t = "| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |\n|---|---:|---:|---:|---:|---:|---|\n"
    for s, v in d["per_path"].items():
        t += f"| {s} | {fmt(v['score'])} | {fmt(v['tracking'])} | {fmt(v['time_score'])} | {fmt(v['v_eq'])} | {fmt(v['mean_abs_stop_err'], 2)} | {', '.join(v['results'])} |\n"
    return t

def hhmm(d):  # '2026-11-18 20:07:33' -> ('2026-11-18','2007')
    day, tm = d["time"].split(); return day, tm[:5].replace(":", "")

index, plain = [], []
if OUT.exists(): shutil.rmtree(OUT)
for src, slug, sweep, p, purpose, obs, extra in E:
    if src is None:   # baseline: no json, numbers from personal_log Step 2b; time from the session transcript (~19:29)
        day, hm, score = "2026-11-18", "1929", 62.3
        folder = OUT / f"{day}_{hm}_{slug}"; folder.mkdir(parents=True)
        (folder / "README.md").write_text(f"""# {day} {hm[:2]}:{hm[2:]} - {slug}

**Sweep/phase:** {sweep}  |  **Score: {score}**  (time is approximate: no report file was written; this was a GUI run)

**Purpose:** {purpose}

| Path | Result | Track /40 | Time /40 | Stop /20 | Score /100 | Stop err (m) |
|---|---|---:|---:|---:|---:|---:|
| straight | stopped | 39.6 | 4.0 | 20.0 | 63.5 | +0.47 |
| wave | stopped | 37.2 | 3.9 | 20.0 | 61.1 | +0.62 |
| lane_change | stopped | 38.9 | 3.9 | 20.0 | 62.9 | +0.62 |
| circle | stopped | 37.9 | 3.9 | 20.0 | 61.8 | +0.48 |

**Parameters:** demo driver, fixed 3 m/s.

**What it showed:** {obs}
""")
        index.append((day, hm, folder.name, sweep, "demo", score, "no files")); continue
    sdir, name = (src.rsplit("/", 1) if "/" in src else (None, src))
    base = SRC / (sdir or "") / name
    d = json.load(open(str(base) + ".json"))
    day, hm = hhmm(d)
    folder = OUT / f"{day}_{hm}_{slug}"; folder.mkdir(parents=True)
    for suf, dst in ((".json", "result.json"), (".png", "report.png"), (".driver.log", "driver.log"), (".sim.log", "sim.log")):
        f = Path(str(base) + suf)
        if f.exists(): shutil.copy(f, folder / dst)
    runs = d["plan"]["repeats"]
    fails = [r for r in d["runs"] if r["result"] != "stopped"]
    note = "\n> Parameters assumed to be the final set N (the run script did not record them).\n" if extra == "assumed" else ""
    (folder / "README.md").write_text(f"""# {day} {hm[:2]}:{hm[2:]} - {slug}

**Phase:** {sweep}  |  **Overall score: {d['overall_score']:.1f}**  |  {runs} run(s) per path, {d['completed_runs']} runs, failures: {len(fails) or 'none'}
{note}
**Purpose:** {purpose}

**What it showed:** {obs}

## Parameters
{ptable(p)}
## Results
{results(d)}
Files: `result.json` (full data), `report.png` (plots){', `driver.log`, `sim.log`' if (folder / 'driver.log').exists() else ''}.
""")
    index.append((day, hm, folder.name, sweep, ",".join(f"{p[k]}" for k in NAMES), d["overall_score"], "ok" if not fails else f"{len(fails)} failed"))

index.sort()
lines = ["| # | Date | Time | Experiment folder | Phase | Score | cruise / lat / brake / aim / gain / base |", "|--:|---|---|---|---|---:|---|"]
for i, (day, hm, name, sweep, ps, sc, st) in enumerate(index, 1):
    ps = ps.replace(",", " / ") if ps != "demo" else "demo driver (3 m/s)"
    lines.append(f"| {i} | {day} | {hm[:2]}:{hm[2:]} | [{name}](experiments/{name}/README.md) | {sweep} | **{sc:.1f}**{' (' + st + ')' if st not in ('ok','no files') else ''} | {ps} |")
(OUT.parent / "timeline.md").write_text("# Experiment timeline (Taiwan time, 2026-11-18)\n\nEvery run in the order it finished. Folder names: `date_time_id_what-it-tested`.\n\n" + "\n".join(lines) + "\n")
print(len(index), "experiments written to", OUT)
