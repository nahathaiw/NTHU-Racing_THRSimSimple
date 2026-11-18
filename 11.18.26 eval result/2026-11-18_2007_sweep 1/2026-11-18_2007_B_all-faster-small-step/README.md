# 2026-11-18 20:07 - B_all-faster-small-step

**Phase:** sweep 1  |  **Overall score: 66.7**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Raise speed limits a little.

**What it showed:** 66.7. Barely better than the defaults.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 16.0 **(changed)** | 12.0 |
| `lat_accel` | 4.0 **(changed)** | 3.0 |
| `brake_decel` | 4.5 **(changed)** | 3.5 |
| `stop_aim` | 2.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 68.6 | 94.6 | 26.9 | 8.1 | 1.51 | stopped, stopped |
| wave | 63.9 | 87.3 | 22.5 | 6.8 | 2.11 | stopped, stopped |
| lane_change | 66.4 | 91.7 | 24.3 | 7.3 | 1.68 | stopped, stopped |
| circle | 67.8 | 97.7 | 21.8 | 6.5 | 2.09 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
