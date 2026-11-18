# 2026-11-18 20:36 - N_brake5.9-aim2.0_BEST

**Phase:** sweep 4  |  **Overall score: 70.3**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Brake 5.9 (just under the car's 6.0 limit) and aim 2.0 to keep the stop inside 5 m.

**What it showed:** 70.3, the best. Straight average speed 10.1 -> 11.6 m/s. Final settings.

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
| straight | 71.8 | 90.9 | 38.7 | 11.6 | 4.59 | stopped, stopped |
| wave | 68.9 | 92.2 | 30.1 | 9.0 | 3.90 | stopped, stopped |
| lane_change | 71.6 | 95.6 | 33.5 | 10.0 | 4.06 | stopped, stopped |
| circle | 68.9 | 96.3 | 25.9 | 7.8 | 2.94 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
