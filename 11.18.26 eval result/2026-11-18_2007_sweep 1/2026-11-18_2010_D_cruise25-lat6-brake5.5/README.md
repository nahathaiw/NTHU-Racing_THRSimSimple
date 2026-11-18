# 2026-11-18 20:10 - D_cruise25-lat6-brake5.5

**Phase:** sweep 1  |  **Overall score: 68.5**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Big step: cruise 25, brake 5.5.

**What it showed:** 68.5. Braking harder was the main gain.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 70.4 | 96.2 | 29.6 | 8.9 | 3.61 | stopped, stopped |
| wave | 66.2 | 85.3 | 30.2 | 9.0 | 4.64 | stopped, stopped |
| lane_change | 69.0 | 93.7 | 28.8 | 8.6 | 4.16 | stopped, stopped |
| circle | 68.4 | 95.6 | 25.4 | 7.6 | 3.95 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
