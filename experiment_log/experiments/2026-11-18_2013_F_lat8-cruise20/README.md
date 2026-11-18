# 2026-11-18 20:13 - F_lat8-cruise20

**Phase:** sweep 1  |  **Overall score: 68.0**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Test a high lateral acceleration limit.

**What it showed:** 68.0. Fine on the circle (69.6) but not better overall.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 20.0 **(changed)** | 12.0 |
| `lat_accel` | 8.0 **(changed)** | 3.0 |
| `brake_decel` | 5.0 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 69.2 | 94.9 | 28.1 | 8.4 | 2.19 | stopped, stopped |
| wave | 64.8 | 85.8 | 26.3 | 7.9 | 2.63 | stopped, stopped |
| lane_change | 68.4 | 93.6 | 27.3 | 8.2 | 2.43 | stopped, stopped |
| circle | 69.6 | 96.3 | 27.6 | 8.3 | 2.72 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
