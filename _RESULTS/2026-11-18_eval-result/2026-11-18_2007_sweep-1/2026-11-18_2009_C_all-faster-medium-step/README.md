# 2026-11-18 20:09 - C_all-faster-medium-step

**Phase:** sweep 1  |  **Overall score: 67.0**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Next step up.

**What it showed:** 67.0.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 20.0 **(changed)** | 12.0 |
| `lat_accel` | 5.0 **(changed)** | 3.0 |
| `brake_decel` | 5.0 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 67.6 | 90.7 | 28.2 | 8.5 | 2.33 | stopped, stopped |
| wave | 64.8 | 87.0 | 24.9 | 7.5 | 3.23 | stopped, stopped |
| lane_change | 67.8 | 93.6 | 26.0 | 7.8 | 2.59 | stopped, stopped |
| circle | 68.0 | 96.2 | 23.7 | 7.1 | 2.99 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
