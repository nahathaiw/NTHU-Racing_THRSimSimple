# 2026-11-18 20:43 - confirm-run-1_final-settings-N

**Phase:** confirmation  |  **Overall score: 70.8**  |  1 run(s) per path, 4 runs, failures: none

> Parameters assumed to be the final set N (the run script did not record them).

**Purpose:** Confirmation run with the final settings (1 run per path).

**What it showed:** 70.85 (single runs, so noisier).

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
| straight | 74.5 | 97.6 | 38.5 | 11.5 | 4.82 | stopped |
| wave | 69.0 | 92.4 | 30.0 | 9.0 | 3.94 | stopped |
| lane_change | 71.2 | 94.9 | 33.1 | 9.9 | 4.10 | stopped |
| circle | 68.7 | 95.9 | 25.9 | 7.8 | 2.88 | stopped |

Files: `result.json` (full data), `report.png` (plots).
