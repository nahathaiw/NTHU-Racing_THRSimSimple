# 2026-11-18 20:38 - P_M-plus-cruise30

**Phase:** sweep 4  |  **Overall score: 70.1**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Higher cruise ceiling.

**What it showed:** 70.1. Tied with N within noise.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 30.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.8 **(changed)** | 3.5 |
| `stop_aim` | 2.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 72.7 | 95.3 | 36.3 | 10.9 | 4.49 | stopped, stopped |
| wave | 68.6 | 91.5 | 30.0 | 9.0 | 4.15 | stopped, stopped |
| lane_change | 70.3 | 92.6 | 33.3 | 10.0 | 4.26 | stopped, stopped |
| circle | 68.9 | 96.5 | 25.6 | 7.7 | 3.27 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
