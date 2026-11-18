# 2026-11-18 20:15 - G_D-plus-gain0.25

**Phase:** sweep 1  |  **Overall score: 68.8**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** D with a shorter lookahead gain (0.40 -> 0.25).

**What it showed:** 68.8, best of sweep 1. Better wave tracking.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 68.4 | 91.5 | 29.6 | 8.9 | 3.46 | stopped, stopped |
| wave | 68.8 | 92.0 | 30.1 | 9.0 | 4.56 | stopped, stopped |
| lane_change | 69.3 | 94.3 | 28.9 | 8.7 | 4.08 | stopped, stopped |
| circle | 68.6 | 96.1 | 25.4 | 7.6 | 3.83 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
