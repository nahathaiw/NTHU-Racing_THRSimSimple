# 2026-11-18 20:22 - J_lat7

**Phase:** sweep 2  |  **Overall score: 68.7**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** More lateral acceleration on top of H.

**What it showed:** 68.7. No gain.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 7.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.25 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 68.9 | 92.4 | 29.8 | 8.9 | 2.95 | stopped, stopped |
| wave | 67.5 | 90.6 | 28.1 | 8.4 | 3.82 | stopped, stopped |
| lane_change | 69.5 | 94.3 | 29.4 | 8.8 | 3.66 | stopped, stopped |
| circle | 68.8 | 95.2 | 26.8 | 8.0 | 3.42 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
