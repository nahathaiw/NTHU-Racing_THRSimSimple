# 2026-11-18 21:04 - confirm-run-2_final-settings-N

**Phase:** confirmation  |  **Overall score: 70.4**  |  1 run(s) per path, 4 runs, failures: none

> Parameters assumed to be the final set N (the run script did not record them).

**Purpose:** Second confirmation / demo run.

**What it showed:** 70.43.

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
| straight | 73.5 | 95.0 | 38.8 | 11.6 | 4.52 | stopped |
| wave | 69.2 | 93.0 | 29.9 | 9.0 | 3.76 | stopped |
| lane_change | 70.5 | 93.2 | 32.9 | 9.9 | 4.13 | stopped |
| circle | 68.6 | 95.7 | 25.9 | 7.8 | 2.93 | stopped |

Files: `result.json` (full data), `report.png` (plots).
