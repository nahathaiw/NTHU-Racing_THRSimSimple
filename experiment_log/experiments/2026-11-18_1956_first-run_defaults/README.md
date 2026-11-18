# 2026-11-18 19:56 - first-run_defaults

**Phase:** first run  |  **Overall score: 66.6**  |  3 run(s) per path, 12 runs, failures: none

**Purpose:** First evaluation of my C++ driver with its default parameters (-n 3).

**What it showed:** Worked first time: 12/12 stopped, none off-track. Time points doubled (4 -> 8.7). Score 66.6.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 12.0 | 12.0 |
| `lat_accel` | 3.0 | 3.0 |
| `brake_decel` | 3.5 | 3.5 |
| `stop_aim` | 1.5 | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 68.2 | 96.1 | 24.4 | 7.3 | 0.61 | stopped, stopped, stopped |
| wave | 64.3 | 90.3 | 20.4 | 6.1 | 0.71 | stopped, stopped, stopped |
| lane_change | 67.1 | 95.1 | 22.8 | 6.8 | 0.58 | stopped, stopped, stopped |
| circle | 66.7 | 97.3 | 19.4 | 5.8 | 0.81 | stopped, stopped, stopped |

Files: `result.json` (full data), `report.png` (plots).
