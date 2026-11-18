# 2026-11-18 21:33 - confirm-run-3_final-settings-N

**Phase:** confirmation  |  **Overall score: 70.2**  |  1 run(s) per path, 4 runs, failures: none

> Parameters assumed to be the final set N (the run script did not record them).

**Purpose:** Third confirmation / demo run.

**What it showed:** 70.15.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.9 **(changed)** | 3.5 |
| `stop_aim` | 2.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 72.1 | 96.4 | 33.9 | 10.2 | 4.78 | stopped |
| wave | 68.7 | 91.9 | 29.9 | 9.0 | 3.71 | stopped |
| lane_change | 70.8 | 93.5 | 33.5 | 10.0 | 4.01 | stopped |
| circle | 69.0 | 96.6 | 25.8 | 7.7 | 2.88 | stopped |

Files: `result.json` (full data), `report.png` (plots).
