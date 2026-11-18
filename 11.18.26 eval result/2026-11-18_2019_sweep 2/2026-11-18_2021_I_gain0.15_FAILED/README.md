# 2026-11-18 20:21 - I_gain0.15_FAILED

**Phase:** sweep 2  |  **Overall score: 47.0**  |  2 run(s) per path, 8 runs, failures: 3

**Purpose:** Is an even shorter lookahead better?

**What it showed:** 47.0: 3 runs left the track. A short lookahead steers about 2x harder for the same error (see 11.18.26 log and diagram/diagrams/2026-11-18_2125_pure-pursuit-geometry.png).

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 25.0 **(changed)** | 12.0 |
| `lat_accel` | 6.0 **(changed)** | 3.0 |
| `brake_decel` | 5.5 **(changed)** | 3.5 |
| `stop_aim` | 3.0 **(changed)** | 1.5 |
| `lookahead_gain` | 0.15 **(changed)** | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 43.5 | 68.9 | 14.8 | 4.4 | 2.88 | stopped, off_track |
| wave | 18.6 | 46.4 | 0.0 | 0.0 | - | off_track, off_track |
| lane_change | 58.2 | 68.4 | 27.1 | 8.1 | 2.71 | stopped, stopped |
| circle | 67.8 | 94.1 | 25.5 | 7.7 | 3.40 | stopped, stopped |

Files: `result.json` (full data), `report.png` (plots), `driver.log`, `sim.log`.
