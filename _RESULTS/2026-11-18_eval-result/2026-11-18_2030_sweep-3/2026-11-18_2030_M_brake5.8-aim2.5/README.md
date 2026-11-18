# 2026-11-18 20:30 - M_brake5.8-aim2.5

**Phase:** sweep 3  |  **Overall score: 69.4**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** K with a smaller stop_aim (3.0 -> 2.5).

**What it showed:** 69.4. Safer stop, same speed.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.8 **(changed)** | 3.5 |
| `stop_aim` | 2.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 69.2 | 89.3 | 33.7 | 10.1 | 4.33 | stopped, stopped |
| wave | 68.6 | 91.2 | 30.2 | 9.1 | 4.16 | stopped, stopped |
| lane_change | 71.3 | 95.0 | 33.4 | 10.0 | 4.39 | stopped, stopped |
| circle | 68.7 | 95.7 | 26.0 | 7.8 | 3.32 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
