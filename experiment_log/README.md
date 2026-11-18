# Experiment log: THRSimSimple driver (2026-11-18)

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
| [experiments/](experiments/) | One folder per experiment: `README.md` (purpose, 6 parameters, per-path results, what it showed), `result.json`, `report.png`, `driver.log`, `sim.log` |
| [personal_log.md](personal_log.md) | The step-by-step learning log: setup, code walkthrough, study notes, decisions |
| [diagrams/](diagrams/) | Explanatory figures (date-time prefixed) |
| [../ARCHITECTURE.md](../ARCHITECTURE.md), [../FLOW.md](../FLOW.md) | How the code works and how data flows |

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
- `eval_results/` (raw output, git-ignored) is the source; `experiment_log/experiments/` is a tracked copy.
  Rebuild with `python3 scripts/build_experiment_log.py`.

## How to add a new experiment

1. Run the sweep or evaluation (results appear in `eval_results/`).
2. Add one line to the list `E` in `scripts/build_experiment_log.py` (source, id, phase, parameters, purpose, what it showed).
3. `python3 scripts/build_experiment_log.py`, then commit.
