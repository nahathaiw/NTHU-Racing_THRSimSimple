# 2026-11-18 20:27 - H2_repeat-of-H

**Phase:** sweep 2  |  **Overall score: 69.4**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Repeat of H to measure noise.

**What it showed:** 69.4 vs 68.9: noise about 0.5.

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
| straight | 69.6 | 94.3 | 29.6 | 8.9 | 2.95 | stopped, stopped |
| wave | 69.1 | 92.5 | 30.2 | 9.0 | 3.92 | stopped, stopped |
| lane_change | 70.2 | 96.2 | 29.2 | 8.8 | 3.70 | stopped, stopped |
| circle | 68.9 | 96.7 | 25.5 | 7.6 | 3.46 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
