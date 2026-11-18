# 2026-11-18 20:01 - repeat-defaults_noise-check

**Phase:** first run  |  **Overall score: 66.3**  |  3 run(s) per path, 12 runs, failures: none

**Purpose:** Same settings again to see run-to-run noise.

**What it showed:** 66.3 vs 66.6: noise is roughly 0.3-0.5 points.

## Parameters
| Parameter | Value | Default |
|---|---:|---:|
| `cruise_speed` | 12.0 | 12.0 |
| `lat_accel` | 3.0 | 3.0 |
| `brake_decel` | 3.5 | 3.5 |
| `stop_aim` | 1.5 | 1.5 |
| `lookahead_gain` | 0.4 | 0.4 |
| `lookahead_base` | 2.5 | 2.5 |

## Results
| Path | Score | Tracking /100 | Time pts /100 | v_eq m/s | Stop err m | Results |
|---|---:|---:|---:|---:|---:|---|
| straight | 68.0 | 95.6 | 24.4 | 7.3 | 0.58 | stopped, stopped, stopped |
| wave | 63.7 | 88.7 | 20.5 | 6.2 | 0.71 | stopped, stopped, stopped |
| lane_change | 66.7 | 94.0 | 22.7 | 6.8 | 0.61 | stopped, stopped, stopped |
| circle | 66.9 | 97.9 | 19.3 | 5.8 | 0.79 | stopped, stopped, stopped |

Files: `result.json` (full data), `report.png` (plots).
