# 2026-11-18 20:37 - O_M-plus-gain0.30

**Phase:** sweep 4  |  **Overall score: 70.1**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Longer lookahead at speed.

**What it showed:** 70.1. Tied with N within noise.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.8 **(changed)** | 3.5 |
| `stop_aim` | 2.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.3 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 73.1 | 93.9 | 38.8 | 11.6 | 4.71 | stopped, stopped |
| wave | 67.9 | 89.8 | 30.0 | 9.0 | 4.45 | stopped, stopped |
| lane_change | 70.7 | 93.6 | 33.2 | 10.0 | 4.74 | stopped, stopped |
| circle | 68.7 | 96.1 | 25.7 | 7.7 | 3.26 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
