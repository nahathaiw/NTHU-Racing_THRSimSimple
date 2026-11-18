# 2026-11-18 20:31 - K2_repeat-of-K

**Phase:** sweep 3  |  **Overall score: 69.5**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Repeat of K.

**What it showed:** 69.5: K's 69.8 was partly noise.

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
| straight | 70.7 | 90.7 | 36.1 | 10.8 | 4.84 | stopped, stopped |
| wave | 68.6 | 91.8 | 29.7 | 8.9 | 4.77 | stopped, stopped |
| lane_change | 70.2 | 92.2 | 33.2 | 10.0 | 4.86 | stopped, stopped |
| circle | 68.7 | 96.1 | 25.5 | 7.7 | 3.67 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
