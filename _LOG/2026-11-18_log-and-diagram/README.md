# Log and diagrams: THRSimSimple driver (2026-11-18)

Everything done on 2026-11-18, organised. All times are Taiwan time (UTC+8). Every experiment folder starts with
`YYYY-MM-DD_HHMM_` (when the run finished), then its id and what it tested.

## Score journey

| Stage | Score |
|---|---:|
| Python demo driver (baseline) | 62.3 |
| First C++ run, default parameters | 66.6 |
| Best of sweep 1 (G) | 68.8 |
| Best of sweep 2 (K, partly luck) | 69.8 |
| Sweep 3 (M, safer stop) | 69.4 |
| **Sweep 4: set N (final)** | **70.3** |
| Confirmation runs with N (1 run per path) | 70.85, 70.43, 70.15 |

Final settings: `cruise_speed 25, lat_accel 6.0, brake_decel 5.9, stop_aim 2.0, lookahead_base 2.5, lookahead_gain 0.25`.
Run-to-run noise is about 0.5 points, so N, O and P (70.3, 70.1, 70.1) are effectively tied.

## What is where

| Path | Content |
|---|---|
| [timeline.md](timeline.md) | All 23 experiments in time order with parameters and score |
| [../2026-11-18_eval-result/](../../_RESULTS/2026-11-18_eval-result/) | Grouped by phase (`..._sweep-1`, `..._sweep-2`, ...), one folder per experiment inside, plus the sweep's `summary.txt`: `README.md` (purpose, 6 parameters, per-path results, what it showed), `result.json`, `report.png`, `driver.log`, `sim.log` |
| [personal_log.md](personal_log.md) | The step-by-step learning log: setup, code walkthrough, study notes, decisions |
| [diagrams/](diagrams/) | Explanatory figures (date-time prefixed) |
| [ARCHITECTURE.md](../../_DOCS/ARCHITECTURE.md), [FLOW.md](../../_DOCS/FLOW.md) | How the code works and how data flows |

## Phases

| Phase | Experiments | Question |
|---|---|---|
| baseline | demo driver | What must we beat? |
| first run | defaults, repeat | Does my controller work, and how noisy is the score? |
| sweep 1 | B to G | How much faster can all limits go? |
| sweep 2 | H to L (+H2) | Safer stop, lookahead gain/base, braking |
| sweep 3 | K2, M | Is K real? Can a smaller stop_aim keep the stop safe? |
| sweep 4 | N, O, P | Final push: brake 5.9, gain 0.30, cruise 30 |
| confirmation | 3 runs | Does N repeat? |

## Notes on accuracy

- The baseline has no report file (GUI run); its numbers come from the log, and its time (about 19:29) is approximate.
- The three confirmation runs did not record their parameters; they are assumed to be the final set N.
- `eval_results/` (raw output, git-ignored) is the source; `_RESULTS/2026-11-18_eval-result/` is a tracked, renamed copy.
  Rebuild with `python3 _SCRIPT/2026-11-18_script/build_experiment_log.py`.

## How to add a new experiment

1. Run the sweep or evaluation (results appear in `eval_results/`).
2. Add one line to the list `E` in `_SCRIPT/2026-11-18_script/build_experiment_log.py` (source, id, phase, parameters, purpose, what it showed).
3. `python3 _SCRIPT/2026-11-18_script/build_experiment_log.py`, then commit.

## Top-level folders

| Folder | Content |
|---|---|
| `_SCRIPT/2026-11-18_script/` | sweep, demo, plot and log-builder scripts |
| `_RESULTS/2026-11-18_eval-result/` | tracked copy of every result, grouped by phase |
| `_LOG/2026-11-18_log-and-diagram/` | this folder: timeline, personal log, diagrams |

Raw output of `evaluate.bash` and the sweep scripts still goes to `eval_results/` (git-ignored); it is the source that the build script copies from.
