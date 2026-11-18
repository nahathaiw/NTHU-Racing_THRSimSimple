# 2026-11-19 00:32 - observe_setN (hint 1: draw the data)

Final set N (cruise 25, lat 6.0, brake 5.9, aim 2.0, gain 0.25, base 2.5), 1 run per path, recorded with
`_SCRIPT/2026-11-19_script/observe.bash setN`. Plots: `01_straight.png` ... `04_circle.png`; raw data in the CSVs.

| Path | Score | Steering delay | Speed delay |
|---|---:|---:|---:|
| straight | 71.8 | 0.17 s | 0.33 s |
| wave | 68.7 | 0.16 s | 0.19 s |
| lane_change | 70.7 | 0.15 s | 0.17 s |
| circle | 68.9 | 0.15 s | 0.27 s |

What the plots show:
- Actual steering arrives about 0.15 s after the command and swings **wider** than the command (circle: command 5-16 deg, actual 0-19 deg).
- On the circle the right steering is a constant 9.5 deg (atan(2.5/15)), but the command oscillates about 1.2 times a second: the feedback loop plus the delay makes the car weave.
- Circle speed is capped at 9.5 m/s by lat_accel 6 (sqrt(6 x 15)); that is the biggest time loss.
- Speed command drops to 0 near the finish, actual takes about 1.3 s to reach 0 (braking limit 6 m/s^2).
