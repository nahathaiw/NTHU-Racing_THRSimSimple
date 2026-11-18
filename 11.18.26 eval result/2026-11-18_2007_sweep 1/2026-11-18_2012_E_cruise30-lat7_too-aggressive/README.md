# 2026-11-18 20:12 - E_cruise30-lat7_too-aggressive

**Phase:** sweep 1  |  **Overall score: 67.7**  |  2 run(s) per path, 8 runs, failures: none

**Purpose:** Even faster in curves.

**What it showed:** 67.7. Tracking error grew (max 0.92 m); more speed stopped paying off.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 30.0 **(changed)** | 12.0 |
| `lat_accel` | 7.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.5 **(changed)** | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 67.8 | 89.7 | 29.7 | 8.9 | 3.57 | stopped, stopped |
| wave | 65.6 | 82.4 | 31.6 | 9.5 | 4.45 | stopped, stopped |
| lane_change | 68.4 | 91.5 | 29.6 | 8.9 | 4.13 | stopped, stopped |
| circle | 68.9 | 95.7 | 26.6 | 8.0 | 4.00 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
