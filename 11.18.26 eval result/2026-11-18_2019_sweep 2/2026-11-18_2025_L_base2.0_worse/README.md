# 2026-11-18 20:25 - L_base2.0_worse

**Phase:** sweep 2  |  **Overall score: 67.7**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Shorter lookahead at standstill.

**What it showed:** 67.7: worse tracking (max 1.06 m). Keep base 2.5.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.0 **(changed)** | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 65.6 | 84.8 | 29.2 | 8.8 | 2.84 | stopped, stopped |
| wave | 68.0 | 91.2 | 28.7 | 8.6 | 3.86 | stopped, stopped |
| lane_change | 68.6 | 92.6 | 28.9 | 8.7 | 3.60 | stopped, stopped |
| circle | 68.5 | 95.8 | 25.5 | 7.6 | 3.47 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
