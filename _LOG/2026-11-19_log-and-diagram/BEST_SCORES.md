# Best scores: how to get each one back

Every entry: score, exact parameters, the script that runs it, and the git tag of the driver code it was measured with.
To go back: `git checkout <tag>` (look only) or `git checkout <tag> -- my_driver/src/driver_node.cpp` (restore the code),
then `colcon build --symlink-install --packages-select my_driver`, then run the script. New parameters always default OFF,
so the newest code also reproduces every older set when given its parameters.

| Rank | Set | Score | Measured | Code tag | Run it |
|---|---|---:|---|---|---|
| **1** | **F15** | **75.5** (3 runs/path, twice; 0 failures; wave 74.3) | 2026-11-19 18:30 `_RESULTS/2026-11-19_eval-result/2026-11-19_1826_c8_ilc_confirm/` | `best-F15-75.5` | `./_SCRIPT/2026-11-19_script/run_best_F15_75.5.bash eval` |
| 2 | B6 | 74.9 (3 runs/path, 48 runs, no failures, stop 1.1-2.9 m) | 2026-11-19 14:47 `_RESULTS/2026-11-19_eval-result/2026-11-19_1447_c6_control_rate/` | `best-B6-74.9` | `./_SCRIPT/2026-11-19_script/run_best_B6_74.9.bash eval` |
| 3 | B5 | 74.9 (E7, 3 runs/path) / 74.4 (C6) | 2026-11-19 14:27 | `best-B6-74.9` | B6 without `control_hz` and with gain 0.10 |
| 4 | R2G10 | 74.2 (2 runs/path, twice) / 74.0 (E7) | 2026-11-19 01:45 | `best-B6-74.9` | `./_SCRIPT/2026-11-19_script/demo_best.bash` of commit `33f3cce` |
| 5 | N | 70.3 | 2026-11-18 20:36 | `best-N-70.3` | `./_SCRIPT/2026-11-18_script/demo_best.bash eval` |

## F15 = B6 + learned steering correction (C8)
All B6 parameters below, plus `ilc_apply true` and `ilc_file _SCRIPT/2026-11-19_script/best_F15_ilc_table.txt` (ilc_gain 0 = frozen,
the file is only read). The table was learned by L15 (ilc_gain 0.15, lead 1.5 m, smooth 2) in 6 runs per path (`2026-11-19_1801_c8_ilc_learn/`).
Note: B6 alone has a rare start off-track on wave / lane change (~3 of 36 runs on 2026-11-19 evening); F15 had none.

## B6 parameters (all of them)
```
cruise_speed 30.0   lat_accel 40.0   brake_decel 5.9   stop_aim 1.5
lookahead_base 2.5  lookahead_gain 0.09               wheelbase 2.5   max_steer 0.6
predict_time 0.10   steer_tau 0.10   steer_rate 1.0   predict_add_age true
steer_mode pp       blend_lqr 0.3    lqr_r 3.0        lqr_q_e 1.0     lqr_q_psi 1.0   lqr_dt 0.05   ff_time 0.10
stop_damp 5.0       bang_brake true  bang_decel 6.0   bang_lead 0.0   bang_cmd -30    bang_release 1.0
control_hz 100
```
Per path (C6, 3 runs): straight 74.9, wave 72.3, lane change 74.2, circle 78.2; tracking 38.3 + time 16.6 + stop 20.0.
