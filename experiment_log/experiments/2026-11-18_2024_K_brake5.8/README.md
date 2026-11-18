# 2026-11-18 20:24 - K_brake5.8

**Phase:** sweep 2  |  **Overall score: 69.8**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Brake closer to the 6 m/s^2 limit.

**What it showed:** 69.8 (partly luck: K2 repeat was 69.5). Time points up.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.8 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 70.1 | 91.1 | 34.0 | 10.2 | 4.86 | stopped, stopped |
| wave | 69.0 | 92.6 | 29.8 | 8.9 | 4.72 | stopped, stopped |
| lane_change | 71.1 | 94.4 | 33.2 | 10.0 | 4.81 | stopped, stopped |
| circle | 69.1 | 97.0 | 25.6 | 7.7 | 3.76 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
