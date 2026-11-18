# 2026-11-18 20:19 - H_G-with-aim3.0

**Phase:** sweep 2  |  **Overall score: 68.9**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** G with a safer stop margin (aim 3.0).

**What it showed:** 68.9.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 68.1 | 90.7 | 29.5 | 8.9 | 2.91 | stopped, stopped |
| wave | 68.9 | 92.2 | 30.2 | 9.1 | 4.02 | stopped, stopped |
| lane_change | 69.8 | 94.8 | 29.6 | 8.9 | 3.78 | stopped, stopped |
| circle | 68.7 | 96.3 | 25.4 | 7.6 | 3.54 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
