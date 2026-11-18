# Next session: how to continue (written 2026-11-19 ~02:50)

## Where we are
- Goal: highest benchmark score with the **official simulator settings** (ceiling about 76; the senior's 92.5 used different
  scoring settings, see personal_log Step 7).
- **Best: set R2G10 = pure pursuit + pose prediction**, 74.2 twice (73.6-74.4 in later same-session checks; noise about 0.6).
  Run it: `./_SCRIPT/2026-11-19_script/demo_best.bash eval`
- Plan + results table: `experiment_plan.md`. One-page status: `MORNING_SUMMARY.md`. Every step: `personal_log.md`.

## Done in the method plan
E1 Stanley 73.0 | E2 predictive Stanley 72.8 | E3 rear-axle Stanley + feed-forward 73.5 | E4 pure pursuit + feed-forward 73.5 |
E5 LQR (kinematic MPC) 73.2 at r=30 (r100 71.5, r300 69.3: stronger steering is better, trend not finished; q_psi 4 helped a little).
None has beaten pure pursuit + prediction so far.

## Still to do (in this order)
1. **E6 LQR tuning first** (trend unfinished): r 3 / 10 / 20, each also with q_psi 4; maybe steer_tau 0.15 in the model. Include E0.
2. **C-rows** (optimise / combine), from `experiment_plan.md`:
   - C1 Stanley with higher K (6-10) and/or with feed-forward: K was still improving at K6.
   - Combination idea: Stanley/LQR on straights (best straight scores) + pure pursuit in curves (best wave/circle).
3. **E7**: 3-run confirmation (`-n 3`) of the best 1-2 settings, same session as R2G10.
4. Optional **E8**: RL-tuned lookahead (RA-L 2026 paper in `_paper/2025-2026/`).
5. Then: update `_DOCS/ARCHITECTURE.md` (new modes, prediction, stop_damp), `START_HERE.md` day row, and the meeting slides.

## How to run a sweep (rules learned the hard way)
```bash
cd ~/Desktop/pleng/NTHU-Racing_THRSimSimple
# 1. nothing else open: no simulator GUI, no demo, no other sweep (sweep.bash checks and refuses)
# 2. write a config file: one line per setting, ID then overrides on top of set N; always include E0 (R2G10) for comparison
./_SCRIPT/2026-11-19_script/sweep.bash NAME _SCRIPT/2026-11-19_script/configs/FILE.txt     # about 1.2 min per setting
```
R2G10 overrides: `lat_accel:=25.0 stop_aim:=1.5 lookahead_gain:=0.10 stop_damp:=2.0 predict_time:=0.10`.
After a code change: `colcon build --symlink-install --packages-select my_driver` (conda deactivated), never while a sweep runs.
Steering modes: `steer_mode:= pp | stanley | stanley_ff | lqr` (parameters listed at the top of `my_driver/src/driver_node.cpp`).
