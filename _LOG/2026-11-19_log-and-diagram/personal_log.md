# Personal Log: goal 95 (from 70.3)

Heading format: `### YYYY-MM-DD HH:MM - Step N: title`. Every experiment gets a date-and-time name.
Previous work (score 70.3, set N): see `_LOG/2026-11-18_log-and-diagram/`.

### 2026-11-19 - Step 1: Folders prepared
Created `_RESULTS/2026-11-19_eval-result/`, `_LOG/2026-11-19_log-and-diagram/`, `_SCRIPT/2026-11-19_script/`. Waiting for the hints to improve the score.

### 2026-11-19 - Step 2: Folders regrouped by the user; paths repaired
User moved everything into `_RESULTS/`, `_LOG/` and `_SCRIPT/` (each holding the 11.18.26 and 11.19.26 folders).
That broke: the scripts' workspace path (`..` -> `../..`), the log builder and plot script output paths, the timeline links, and doc references. All repaired and re-tested (builder rebuilt 23 experiments, plot script ran, bash syntax ok).
Recreated `_RESULTS/2026-11-19_eval-result/README.md` (the folder was missing after the move). Note: the 11.18.26 personal log is now named `personal_log.md` (no space), kept as the user named it.

### 2026-11-19 - Step 3: Cleaner names and one front door
Renamed for consistent, sortable names without spaces: `_All_Results` -> `_RESULTS`; day folders `11.18.26 script` -> `2026-11-18_script`, `... eval result` -> `2026-11-18_eval-result`, `... log and diagram` -> `2026-11-18_log-and-diagram` (same for 11.19); phases `first run`/`sweep 1` -> `first-run`/`sweep-1`; `11.18.26personal_log.md` -> `personal_log.md`.
Moved `ARCHITECTURE.md` and `FLOW.md` to `_DOCS/`. Added `START_HERE.md` (map of folders, days, commands). Updated all paths; rebuilt the timeline (23 experiments), re-ran the plot script, checked bash syntax and all markdown links (none broken).

### 2026-11-19 - Step 4: Hints received, understanding them (no code changed)

**Hints from the lead:** draw the data and observe it; find the reason and fix it; plot the data; key hint: predict;
models that help: pure pursuit, bicycle model; add a steering delay.

**How they fit together (one idea):** the car does not react instantly. Steering follows the command through a PI loop
(wn 10 rad/s, max 1 rad/s), speed through a slower one (wn 3 rad/s), the pose is up to 20 ms old and a command lasts 50 ms.
So the driver steers for where the car *was*, and the real wheel angle arrives late -> overshoot and wiggle at speed
(why set I failed, why lat_accel had to stay at 6). Fix: (1) plot commanded vs actual steering/speed to *measure* the delay,
(2) use the bicycle model to *predict* where the car will be when the command takes effect, with the steering
following the command with that delay, (3) run pure pursuit from the predicted pose.

**Ceiling check (important):** with the official settings the score cannot reach 95.
time = 40 x v_eq/30, v_eq = path length / time until at rest. Best possible profile (accel 20, brake 6 m/s^2, stop 5 m past):
| Path | length | v_eq max | time max /40 | N now |
|---|---:|---:|---:|---:|
| straight | 60.0 | 11.3 | 15.1 | 15.4 (at the ceiling) |
| wave | 65.5 | 11.9 | 15.8 | 12.0 |
| lane_change | 61.0 | 11.4 | 15.2 | 13.3 |
| circle | 94.2 | 14.4 | 19.2 | 10.4 |
Average time max about 16.3/40 -> best possible total about 40 + 16.3 + 20 = **76** (perfect tracking, ideal actuators).
Current 70.3. Realistic room: tracking +1 to 2, time mostly on circle and wave (+2 to 3). Need to ask the lead what "95" means.

### 2026-11-19 00:32 - Step 5: Observe the data (hint 1) -> `_RESULTS/2026-11-19_eval-result/2026-11-19_0032_observe_setN/`

New scripts: `_SCRIPT/2026-11-19_script/record_run.py` (records /veh_ctrl, /veh_actual, /veh_state per run; plots speed, steering,
cross-track error, top view; measures the delay) and `observe.bash` (driver with set N + recorder + headless evaluation, 1 run per path).
Scores 71.8 / 68.7 / 70.7 / 68.9. Measured steering delay **0.15-0.17 s**, speed delay 0.17-0.33 s.

**Reason found:** the steering loop in `sim.yaml` is `steer_kp 4.0, steer_ki 50.0`, i.e. wn = sqrt(50) = 7.1 rad/s and
zeta = 4 / (2 x 7.1) = **0.28** (the comment says zeta 0.8, wn 10, which does not match the numbers). An under-damped loop:
the actual steering overshoots the command. With 0.15 s of delay, pure pursuit keeps correcting late, so the car weaves
(clear on the circle: the needed steering is a constant 9.5 deg, the command oscillates about 1.2 Hz). Speed loop: wn 3, zeta 1.33 (slow, no overshoot).

**Senior's result (92.5 = tracking 32.5 + time 40 + stop 20, speed 30):** with this simulator, time 40/40 needs v_eq = 30 m/s,
i.e. 60 m in 2.0 s *including stopping*. Even without braking, max_accel 20 m/s^2 covers only 0.5 x 20 x 2^2 = 40 m in 2 s,
and braking from 30 m/s at 6 m/s^2 takes 5 s and 75 m. So that result must come from a different simulator version or
settings (max_decel, time_v_max, path_length or the time formula). To ask the senior: which commit/version, his sim.yaml, and the JSON report.

### 2026-11-19 - Step 6: Checked the ceiling with the simulator's own model
The senior believes he used the same version and says the key is to predict the route.
`_SCRIPT/2026-11-19_script/ceiling_check.py` drives the simulator's own `BicycleModel` (same sim.yaml values) perfectly on the
straight: full throttle, then full braking at the best point, stop inside 55-65 m. Result: peak 22.8 m/s, at rest after 4.94 s,
**v_eq 12.15 m/s -> time 16.2/40**. 40/40 needs v_eq 30 (at rest after 2.0 s), impossible with accel 20 / brake 6 m/s^2.
The straight has no curves, so predicting the route cannot change this number.
Most likely explanation: a different `time_v_max` (or other scoring setting) in his run; e.g. time_v_max 12 would give 40/40 at v_eq 12.
To settle it: ask for his JSON report (it lists `v_eq` and `time` per run).
Predicting the route is still the right next step for tracking and curves (wave, circle).

### 2026-11-19 - Step 7: Senior's screenshot (92.5) analysed
Screenshot: overall 92.5 = tracking 32.5 + time 40.0 + stop 20.0, **12 runs, mean v_eq 22.4 m/s**; last run (circle) at rest after 4.4 s.
- With `time_v_max` 30, time = 40 x min(v_eq, 30)/30, so a mean v_eq of 22.4 can give at most 40 x 22.4/30 = **29.9/40**.
  40.0/40 means every run reached time_v_max, so his time_v_max was **at most the slowest run's v_eq, below 22.4** (not 30).
- Mean v_eq 22.4 is also far above what the car can do with accel 20 / brake 6 (perfect straight 12.2, perfect circle about 14).
  Circle 94 m with rest after 4.4 s fits much harder braking (about 20 m/s^2). So the vehicle limits were likely different too.
- Trail on the circle runs about 1 m inside the path (corner cutting at high speed) -> tracking 32.5 fits.
Check: in his window click "? Scoring rules"; it prints `Time = 40 x min(v_eq, X) / X` with his real X. Also compare his
`simulator/thr_sim/config/sim.yaml` (max_decel, max_accel, time_v_max) with ours (6, 20, 30).

### 2026-11-19 00:49 - Step 8: Prediction added to the driver; sweep p1 (first attempt INVALID)
Code (`8aab22c`): `predict()` steps the bicycle model forward `predict_time` s from the actual pose, speed and wheel angle;
the wheel moves toward the last command with lag `steer_tau` 0.10 s, at most `steer_rate` 1 rad/s; plus the pose message age.
Pure pursuit then runs from the predicted pose. `predict_time 0` = exactly set N.
New script `_SCRIPT/2026-11-19_script/sweep.bash NAME CONFIG_FILE` (set N + overrides per line, dated folders, summary.txt).
**First attempt invalid:** an interrupted launch left an evaluation running, so two sweeps ran at once (two drivers on one car):
everything off-track, even N0. Folder kept as `2026-11-19_0049_p1_predict_time_INVALID-two-sweeps-at-once`. Lesson: before a
sweep, check nothing else is running (`pgrep -af "[e]valuate|[m]y_driver"`).

### 2026-11-19 ~01:05 - Step 9: Sweep p1 results (clean re-run, 2 runs per path)
| Config | predict_time | Score | Track | Time | Max err | Wave |
|---|---:|---:|---:|---:|---:|---:|
| N0 | 0 (set N) | 69.8 | 37.3 | 12.6 | 0.55 | 68.6 |
| P10 | 0.10 | 69.8 | 37.0 | 12.8 | 0.56 | 67.0 |
| P15 | 0.15 | 69.4 | 36.9 | 12.5 | 0.61 | 65.7 |
| P20 | 0.20 | 68.8 | 36.0 | 12.8 | 0.78 | 64.5 |
| P25 | 0.25 | 68.3 | 35.8 | 12.5 | 1.11 | 62.9 |
**Prediction alone does not help at set N's speeds;** more prediction makes the wave worse. Likely reason: pure pursuit already
looks ahead (ld about 8.75 m), and predicting first moves the aim point even further ahead, so the car cuts the wave's corners.
Prediction should matter when the car goes faster in curves. Next: sweep p2, raise lat_accel (curve speed) with and without prediction.

### 2026-11-19 ~01:15 - Step 10: Sweep p2 results: faster curves (lat_accel), with and without prediction
| Config | lat_accel | predict | gain | Score | Track | Time | Stop | Max err | Failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| L9 | 9 | 0 | 0.25 | 70.4 | 36.6 | 13.8 | 20.0 | 0.86 | none |
| L12 | 12 | 0 | 0.25 | 69.3 | 36.1 | 13.2 | 20.0 | 1.00 | none |
| L16 | 16 | 0 | 0.25 | 64.1 | 33.6 | 13.0 | 17.5 | 2.05 | **wave off_track** |
| L12P10 | 12 | 0.10 | 0.25 | 70.2 | 36.6 | 13.6 | 20.0 | 0.83 | none |
| L16P10 | 16 | 0.10 | 0.25 | 71.5 | 36.6 | 14.9 | 19.9 | 1.03 | none |
| **L16P10G** | 16 | 0.10 | 0.20 | **72.0** | 37.2 | 14.8 | 20.0 | 0.82 | none |
**This is where prediction pays off:** at lat_accel 16 the car leaves the track on the wave WITHOUT prediction (L16), and stays
on it WITH prediction (L16P10). Prediction makes faster curves stable, and faster curves bring time points (12.6 -> 14.8).
With prediction a shorter lookahead (0.20) also works and tracks better. New best **72.0** (old 70.3).
Per path now: straight 11.6 m/s (at the ceiling), wave 11.0 (ceiling 11.9), lane 11.4 (ceiling 11.4), circle 10.5 (ceiling 14.4).
Watch: stop errors 4.6-4.7 m on straight/wave/lane, close to the 5 m limit.
Next: sweep p3 around L16P10G (lat 20/25, predict 0.15, gain 0.15).

### 2026-11-19 ~01:25 - Step 11: Sweep p3 results (around the p2 best)
| Config | lat | predict | gain | Score | Track | Time | Max err | Note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| A16 | 16 | 0.10 | 0.20 | 71.7 | 36.9 | 14.8 | 0.74 | repeat of L16P10G (72.0): noise |
| A20 | 20 | 0.10 | 0.20 | 71.1 | 37.1 | 14.0 | 0.83 | wave/lane about 1 s slower (!) |
| A25 | 25 | 0.10 | 0.20 | 72.1 | 36.8 | 15.5 | 0.86 | fastest; stop err up to 5.2 m |
| A20P15 | 20 | 0.15 | 0.20 | 70.6 | 36.5 | 14.0 | 0.91 | |
| **A16G15** | 16 | 0.10 | 0.15 | **72.3** | 37.4 | 14.8 | 0.61 | best; gain 0.15 failed without prediction (set I) |
| A20P15G15 | 20 | 0.15 | 0.15 | 71.3 | 37.2 | 14.1 | 0.79 | |
predict_time 0.10 is better than 0.15. Gain 0.15 now works (set I failed 3 runs without prediction): prediction fixed that.

### 2026-11-19 01:27 - Step 12: Found the "1 s slower" reason: the car rolls backward after stopping
`observe_A20` (`_RESULTS/2026-11-19_eval-result/2026-11-19_0127_observe_A20/`): after the command drops to 0 the actual
speed undershoots to about -0.13 to -0.17 m/s, so the car rolls back 10-15 cm over more than a second. The simulator calls a
run "stopped" only after the car moved < 5 cm for 1 s, so the roll adds about **1 s** to the run time. Measured on all 8
recorded runs: about 1 s lost whenever min speed < -0.13 (set N circle; A20 wave, lane, circle), about 0 otherwise.
Offline test with the sim's speed loop and no noise (`stop_creep_test.py`) does not show it, so it depends on noise/timing.
Fix (driver, param `stop_damp`, 0 = off): after the finish, if the car rolls backward, command `min(1, -stop_damp * v_actual)`
forward. Next: sweep p4 tests stop_damp 0/2/5 on A16G15 and A25.

### 2026-11-19 ~01:36 - Step 13: Sweep p4 results: stop_damp (cancel the backward roll)
| Config | base | stop_damp | Score | Track | Time | Stop | Circle v_eq | Worst stop err |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| G15D0 | A16G15 | 0 | 72.4 | 37.6 | 14.8 | 20.0 | 10.4 | 4.8 |
| **G15D2** | A16G15 | 2 | **72.8** | 37.5 | 15.2 | 20.0 | **12.0** | 4.8 |
| G15D5 | A16G15 | 5 | 72.7 | 37.4 | 15.3 | 20.0 | 12.0 | 4.8 |
| A25D0 | A25 | 0 | 72.4 | 37.1 | 15.5 | 19.9 | 11.6 | 5.1 |
| A25D2 | A25 | 2 | 72.6 | 37.0 | **16.0** | 19.6 | **13.4** | 5.2 |
| A25D5 | A25 | 5 | 72.1 | 36.8 | 15.9 | 19.4 | 13.4 | 5.3 |
**The roll fix works:** circle v_eq +1.6 m/s (lat 16) and +1.8 m/s (lat 25; 13.4 vs ceiling 14.4). stop_damp 2 is enough.
A25D2 has the highest time (16.0) but loses stop points: stop errors 5.0-5.2 m, just past the 5 m free zone.
-> p5 (queued) tests stop_aim 1.5 with lat 25.

### 2026-11-19 ~01:45 - Step 14: Sweep p5 results: faster curves with the roll fixed (base G15D2)
| Config | lat | predict | aim | Score | Track | Time | Stop | Circle v_eq | Worst stop err |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q16A15 | 16 | 0.10 | 1.5 | 73.0 | 37.6 | 15.4 | 20.0 | 12.1 | 4.2 |
| Q20 | 20 | 0.10 | 2.0 | 73.1 | 37.3 | 15.8 | 20.0 | 12.8 | 4.6 |
| Q25 | 25 | 0.10 | 2.0 | 73.2 | 37.2 | 16.0 | 20.0 | 13.4 | 4.9 |
| **Q25A15** | 25 | 0.10 | 1.5 | **73.6** | 37.5 | 16.1 | 20.0 | 13.5 | 4.7 |
| Q30 | 30 | 0.10 | 2.0 | 73.3 | 37.4 | 16.1 | 19.7 | 13.8 | 5.2 |
| Q25P05 | 25 | 0.05 | 2.0 | 73.5 | 37.4 | 16.0 | 20.0 | 13.4 | 4.8 (best wave 72.4, max err 0.45) |
- The "1 s slower at lat 20" problem is gone (Q20 wave 11.4, lane 11.6 m/s): it was the backward roll.
- stop_aim 1.5 keeps the stop inside 5 m at no time cost. New best **73.6** (Q25A15).
- **Time 16.1/40 is at the ceiling (about 16.3).** v_eq: straight 11.6, wave 11.5, lane 11.6, circle 13.5.
  What is left: tracking 37.5 -> 40 (about 2.5 points). Next: sweep p6 on tracking (predict 0.05, gain 0.10, base 2.0, steer_tau 0.15).

### 2026-11-19 ~01:55 - Step 15: Sweep p6 results: tracking (base Q25A15)
| Config | change | Score | Track | Time | Max err | Failures |
|---|---|---:|---:|---:|---:|---|
| R0 | repeat of Q25A15 (73.6) | 73.5 | 37.6 | 16.0 | 0.92 | none |
| R1P05 | predict 0.05 | 73.6 | 37.5 | 16.1 | 0.71 | none |
| **R2G10** | gain 0.10 | **74.2** | **38.2** | 16.0 | 0.56 | none |
| R3P05G10 | predict 0.05 + gain 0.10 | 58.7 | 31.5 | 12.2 | 2.09 | **wave off_track x2** |
| R4B20 | base 2.0 | 74.0 | 38.0 | 16.0 | 0.65 | none |
| R5T15 | steer_tau 0.15 | 73.6 | 37.6 | 16.0 | 0.71 | none |
New best **74.2** (R2G10). A shorter lookahead tracks better, BUT only with enough prediction: gain 0.10 works with
predict 0.10 and fails with predict 0.05 (R3). Same lesson as set I: prediction is what makes a short lookahead stable.
Next: sweep p7 around R2G10 (base 2.0, gain 0.08, predict 0.12/0.15).

### 2026-11-19 ~02:00 - Step 16: Sweep p7 results: around R2G10 -> plateau at about 74.2
| Config | change from R2G10 | Score | Track | Time | Max err |
|---|---|---:|---:|---:|---:|
| S0 | repeat of R2G10 (74.2) | 74.2 | 38.2 | 16.0 | 0.51 |
| S1B20 | base 2.0 | 74.1 | 38.1 | 16.0 | 0.48 |
| S2G08 | gain 0.08 | 74.3 | 38.2 | 16.1 | 0.47 |
| S3P15 | predict 0.15 | 73.5 | 37.5 | 16.0 | 0.82 |
| S4P15G08 | predict 0.15 + gain 0.08 | 74.1 | 38.1 | 16.0 | 0.65 |
| S5P12 | predict 0.12 | 73.9 | 37.8 | 16.1 | 0.50 |
Parameter tuning has flattened: everything within noise of 74.2. R2G10 repeated exactly (74.2 twice), so it is the
**current best set "R2G10"**: cruise 25, lat_accel 25, brake 5.9, stop_aim 1.5, lookahead_base 2.5, lookahead_gain 0.10,
predict_time 0.10, steer_tau 0.10, steer_rate 1.0, stop_damp 2.0. predict_time 0.10 is the sweet spot (0.05 unstable, 0.15 worse).
Score journey today: 70.3 (set N) -> 72.0 (prediction + faster curves) -> 72.8 (roll fix) -> 73.6 (stop_aim) -> 74.2 (short lookahead).
Remaining gap to the ceiling (about 76) is tracking (38.2/40). More tuning will not find it; a code change would (e.g. curvature feed-forward steering).

### 2026-11-19 - Step 17: Live demo script for set R2G10
`./_SCRIPT/2026-11-19_script/demo_best.bash [eval [RUNS] | straight|wave|lane_change|circle]` starts my_driver with R2G10 and opens the GUI.

### 2026-11-19 02:08 - Step 18: Downloaded papers into `_paper/`
9 PDFs (Coulter 1992, Snider 2009, Lipp & Boyd 2014, Kapania & Gerdes 2015, Paden 2016, Kabzan/AMZ 2020, O'Kelly/F1TENTH 2020,
Betz 2022, Becker 2023), each checked by reading its title page. Not found free: Hoffmann 2007 (Stanley), Kong 2015, Rajamani book.
`_paper/README.md` has the reading order, links and what each paper means for my_driver. PDFs are git-ignored (40 MB, copyright).
Read first: Snider 2009 (explains the sweeps), Kapania & Gerdes 2015 (feed-forward steering, the next step).

### 2026-11-19 ~02:20 - Step 19: Found new (2025-2026) methods that cite the classics
OpenAlex: 1,603 papers from 2025-2026 cite our reading list; 501 are about vehicle path tracking / racing control
(learning-based 213, MPC 164, improved pure pursuit 133, delay compensation 46, speed profile 43).
Key filter: our simulator is kinematic (no tyres), so tyre/friction papers do not apply; prediction + kinematic MPC + learned lookahead do.
Downloaded 8 PDFs to `_paper/2025-2026/` with a README (classification, fit rating, implement order).
Implement order: (1) predictive Stanley + feed-forward (DLR 2026), (2) kinematic MPC with steering lag (MAP2 / LPV-MPC / FS 2026),
(3) RL-tuned lookahead (RA-L 2026).

### 2026-11-19 ~02:25 - Step 20: Experiment plan for the new methods
Plan and results table: `_LOG/2026-11-19_log-and-diagram/experiment_plan.md`. E0 baseline R2G10 (74.2); E1 Stanley; E2 predictive
Stanley; E3 predictive Stanley + feed-forward; E4 pure pursuit + feed-forward; E5 kinematic MPC with steering lag (LQR form);
E6 tuned MPC; E7 best + 3-run confirmation; E8 optional RL lookahead. All aim at tracking (38.2/40); filled in step by step.

### 2026-11-19 ~02:35 - Step 21: Steering modes implemented (E1-E4 code), E1 sweep started
Read the DLR 2026 thesis (`_paper/2025-2026/2026_DLR_Predictive_Stanley_Feedforward.pdf`, ch. 3) and implemented its control laws in
`driver_node.cpp` (`66e2f07`), switchable with `steer_mode`:
- `stanley` (eq. 3.4-3.5): delta = psi + atan(K e / (K_prot + v)) at the FRONT axle; psi = path heading - car heading, e = sideways
  error. Optional yaw-rate damping (Hoffmann 2007): + K_yaw (v kappa - v tan(steer)/L).
- predictive Stanley (eq. 3.12-3.14): `stanley_pred_steps` N > 0: Stanley on the current state and N predicted states (bicycle model
  + steering lag, step `stanley_pred_dt`), weighted sum with weights decay^k normalised to 1.
- `stanley_ff` (enhanced Stanley, sec. 3.4-3.5): Stanley at the REAR axle + feed-forward atan(L kappa) at v * ff_time ahead.
- `pp` + `ff_gain` (Kapania & Gerdes 2015): blend pure pursuit with the feed-forward steering.
Needed: signed path curvature `kappa_s_`, path heading at s, and `roll()` (the prediction model, reused by predictive Stanley).
Default `steer_mode pp` = R2G10 unchanged. E1 sweep: E0 (R2G10), Stanley K2 without/with prediction, K1, K4, K2 + yaw damping.

### 2026-11-19 ~02:40 - Step 22: E1 first attempt INVALID (another experiment was open) -> guard added, re-run
The user had another experiment open during E1. Proof: E0 (= R2G10, 74.2 twice) went off-track on all 8 runs (13.2).
Stopped everything, checked `ros2 node list` empty, kept the folder as `2026-11-19_0217_e1_stanley_INVALID-another-experiment-open`.
**Guard added to `sweep.bash`:** it refuses to start, and stops before each config, if another driver, simulator, GUI, evaluation or
demo is running (waits up to 10 s for the previous run to shut down). Second time this happened today (first: Step 8).
Rule: while a sweep runs, do not open the GUI / demo. E1 re-run started.

### 2026-11-19 02:21 - Step 23: E1 results: Stanley (clean re-run, `2026-11-19_0221_e1_stanley/`)
| Config | Steering | predict | Score | Track | Max err | Failures |
|---|---|---:|---:|---:|---:|---|
| E0 | pure pursuit (R2G10) | 0.10 | **73.6** | 37.7 | 0.57 | none |
| E1K2P0 | Stanley K2, paper version | 0 | 50.7 | 27.9 | 2.16 | wave x2, lane off_track |
| E1K2 | Stanley K2 | 0.10 | 72.6 | 36.5 | 0.69 | none |
| E1K1 | Stanley K1 | 0.10 | 71.5 | 35.4 | 0.84 | none |
| E1K4 | Stanley K4 | 0.10 | 73.0 | 36.9 | 0.51 | none |
| E1K2Y | Stanley K2 + yaw damping 0.05 | 0.10 | 72.4 | 36.3 | 0.74 | none |
- E0 = 73.6 here vs 74.2 earlier: noise between sweeps about 0.6 (so compare within the same sweep).
- Stanley without prediction is unstable at our speeds (the 0.15 s lag), like pure pursuit was: prediction is required.
- With prediction Stanley is about 0.6 below pure pursuit; a higher K tracks better (K1 < K2 < K4). Yaw damping did not help.
Next: E2 predictive Stanley (horizon N 3/6, decay 0.5/0.7) and K6.

### 2026-11-19 02:28 - Step 24: E2 results: predictive Stanley (`2026-11-19_0228_e2_predictive_stanley/`)
| Config | Steering | Score | Track | Max err |
|---|---|---:|---:|---:|
| E0 | pure pursuit (R2G10) | **74.0** | 38.0 | 0.59 |
| E2K6 | Stanley K6 | 73.2 | 37.2 | 0.47 |
| E2K4N3 | predictive Stanley K4, 3 steps, decay 0.7 | 72.2 | 36.3 | 0.69 |
| E2K4N6 | predictive Stanley K4, 6 steps, decay 0.7 | 71.8 | 35.8 | 0.95 |
| E2K4N3D5 | predictive Stanley K4, 3 steps, decay 0.5 | 72.5 | 36.6 | 0.66 |
| E2K6N3 | predictive Stanley K6, 3 steps | 72.8 | 36.7 | 0.60 |
**Predictive Stanley made Stanley worse here** (longer horizon = worse). Likely reason: our `predict_time` already compensates the
delay; the extra horizon averages in commands for future states, which makes the steering slower to react. This differs from the
DLR thesis, whose base Stanley had no latency compensation. Pure pursuit + prediction stays best (74.0).
Next: E3 (rear-axle Stanley + feed-forward) and E4 (pure pursuit + feed-forward) in one sweep.

### 2026-11-19 ~02:45 - Step 25: New rule: optimise promising methods and try combinations
User: if a method has high potential, optimise it; if methods are better combined, combine them. Added a "C-rows" table to
`experiment_plan.md`: a method within noise (~0.6) of the best, or best on some path, gets an optimisation round; methods good at
different things get combined. First candidate C1: Stanley with higher K (trend still rising at K6; best straight 74.6).

### 2026-11-19 ~02:50 - Step 26: E5 code: kinematic MPC as LQR (written while E3/E4 runs); overnight run requested
User asked to keep running experiments overnight. E5 implemented (`steer_mode lqr`): state x = [e, psi_e, steer - steer_ff]
(sideways error, heading error, wheel angle minus the feed-forward angle), model e' = v psi_e, psi_e' = v/L (steer - steer_ff),
steer' = (u - steer)/tau (the steering lag). Without constraints, MPC with a long horizon = LQR: K from the discrete Riccati
equation (value iteration, 3x3, recomputed each cycle for the current speed). Command u = atan(L kappa(ahead)) - K x, from the
PREDICTED pose and wheel angle. Offline check (numpy): closed loop stable 5-20 m/s; r = 1 is far too aggressive (37 deg per metre
of error), r = 30-300 gives 3-10 deg/m (pure pursuit about 4). E5 sweep: r 30/100/300, ff_time 0.2, q_psi 4.

### 2026-11-19 02:36 - Step 27: E3/E4 results: feed-forward (`2026-11-19_0236_e3e4_feedforward/`)
| Config | Steering | Score | Track | Max err | Wave | Circle |
|---|---|---:|---:|---:|---:|---:|
| E0 | pure pursuit (R2G10) | **73.9** | 37.9 | 0.63 | 71.6 | 76.3 |
| E3K4F10 | rear-axle Stanley K4 + ff 0.10 s | 73.5 | 37.5 | 0.75 | 70.9 | 75.7 |
| E3K4F20 | rear-axle Stanley K4 + ff 0.20 s | 73.2 | 37.2 | 0.92 | 69.7 | 76.0 |
| E3K2F10 | rear-axle Stanley K2 + ff 0.10 s | 73.1 | 37.1 | 0.76 | 69.7 | 75.8 |
| E4G3 | pure pursuit + 30 % feed-forward | 73.5 | 37.4 | 0.69 | 70.8 | 76.1 |
| E4G5 | pure pursuit + 50 % feed-forward | 72.1 | 36.3 | 0.87 | 67.8 | 75.1 |
| E4G3F20 | pure pursuit + 30 % ff, 0.20 s | 73.2 | 37.3 | 0.79 | 69.5 | 75.9 |
No feed-forward variant beats plain pure pursuit + prediction. The enhanced (rear-axle) Stanley with feed-forward is the best
Stanley so far (73.5) and within noise of pure pursuit. More feed-forward makes the WAVE worse: on the wave the curvature changes
all the time, and our curvature estimate from nodes 1 m apart plus the preview point is never exactly where the car is.
Lesson so far: pure pursuit + our pose prediction already captures what these papers add for THIS simulator (kinematic, no tyres).
Next: E5 LQR (running), then C-rows.

### 2026-11-19 ~02:50 - Step 28: Paused for the night (user needs credits); E5 finished first
User asked to stop and continue next session, after the latest experiment. I first stopped the queue too early (E5 part 1 cut
off during E5R100), then restarted the 4 remaining E5 settings as `e5_lqr_part2`. E5 part 1 (`2026-11-19_0245_e5_lqr/`):
E0 74.4 (track 38.3), E5R30 73.2 (track 37.1); `..._E5R100_INVALID-interrupted` discarded.
Handoff for tomorrow: `_LOG/2026-11-19_log-and-diagram/NEXT_SESSION.md` (where we are, remaining work in order, sweep rules).

### 2026-11-19 02:48 - Step 29: E5 results: kinematic MPC as LQR (`2026-11-19_0245_e5_lqr/` + `2026-11-19_0248_e5_lqr_part2/`)
| Config | r | ff_time | q_psi | Score | Track | Max err |
|---|---:|---:|---:|---:|---:|---:|
| E0 (pure pursuit, R2G10) | | | | **74.4** | 38.3 | 0.56 |
| E5R30 | 30 | 0.10 | 1 | 73.2 | 37.1 | 0.57 |
| E5R100 | 100 | 0.10 | 1 | 71.5 | 35.5 | 0.85 |
| E5R300 | 300 | 0.10 | 1 | 69.3 | 33.2 | 1.60 |
| E5R100F20 | 100 | 0.20 | 1 | 70.2 | 34.7 | 1.27 |
| E5R100Q4 | 100 | 0.10 | 4 | 71.8 | 35.7 | 0.97 |
No failures. **The smaller r (stronger steering), the better, and the trend has not stopped at r = 30**, so E5 is not finished:
next session E6 tries r 3/10/20 (+ q_psi 4). LQR at r 30 (73.2) is about 1 point below pure pursuit, the same gap as Stanley.
All of today's methods stay below pure pursuit + prediction so far. Paused here for the night; plan in `NEXT_SESSION.md`.

### 2026-11-19 13:52 - Step 30: Session resumed; E6 LQR tuning started
Resumed from `NEXT_SESSION.md`. E6 continues the E5 trend (smaller r = stronger steering = better): r 20/10/3, r10 + q_psi 4,
r10 + steer_tau 0.15 (shared with the prediction). Offline check at 12 m/s: r20 11, r10 16, r3 27 deg per metre, all stable.

### 2026-11-19 13:52 - Step 31: E6 results: LQR tuning (`2026-11-19_1352_e6_lqr_tuning/`)
| Config | Change | Score | Track | Max err | Straight | Wave | Circle |
|---|---|---:|---:|---:|---:|---:|---:|
| E0 | pure pursuit (R2G10) | **73.9** | 37.8 | 0.70 | 74.4 | 71.4 | 76.0 |
| E6R20 | LQR r 20 | 73.7 | 37.6 | 0.53 | 74.0 | 70.9 | 75.7 |
| E6R10 | LQR r 10 | 72.2 | 36.2 | 0.82 | 70.9 | 72.1 | 74.0 |
| E6R3 | LQR r 3 | 73.0 | 37.0 | 0.65 | 72.3 | **72.6** | 73.6 |
| E6R10Q4 | r 10, q_psi 4 | 72.9 | 36.9 | 0.58 | 72.9 | 71.7 | 74.4 |
| E6R10T15 | r 10, steer_tau 0.15 | 70.8 | 34.8 | 0.90 | 71.4 | 69.8 | 71.1 |
LQR's best is r 20-30 (73.7, within noise of pure pursuit 73.9, smallest max error 0.53 m). Strong LQR (r 3-10) gives the best
WAVE of any method so far but loses on the straight and circle. -> by the rule: combine. Added `blend_lqr` (pure pursuit mixed with
LQR). Next sweep: C1 Stanley K8/K12, C2 blends 0.3/0.5 with r 20 and r 3.
Senior discussion (chat, 13:55): user says the senior used the same settings with a different algorithm. Explained the check that
holds for any algorithm: through /veh_ctrl, accel 20 m/s^2 covers at most 40 m in 2 s, but time 40/40 on the straight needs
60 m + stop in 2 s; and mean v_eq 22.4 with time 40/40 is impossible with time_v_max 30. Asked for his JSON / driver topics / code.

### 2026-11-19 14:00 - Step 32: C1/C2 results (`2026-11-19_1400_c1c2_combine/`) + ceiling corrected to 77.5
| Config | Steering | Score | Track | Max err | Straight | Wave | Lane | Circle |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| E0 | pure pursuit (R2G10) | 74.0 | 38.0 | 0.52 | 74.5 | 71.9 | 73.3 | 76.3 |
| C1K8 | Stanley K8 | 73.3 | 37.4 | 0.45 | 74.6 | 71.4 | 73.6 | 73.8 |
| C1K12 | Stanley K12 | 73.7 | 37.6 | **0.35** | 74.6 | 72.1 | **74.1** | 74.0 |
| C2B3R20 | pp + 30 % LQR r20 | 74.0 | 37.9 | 0.67 | **74.8** | 70.8 | 73.7 | 76.5 |
| C2B5R20 | pp + 50 % LQR r20 | 73.6 | 37.6 | 0.68 | 74.3 | 70.6 | 73.0 | 76.5 |
| **C2B3R3** | pp + 30 % LQR r3 | **74.3** | **38.3** | 0.61 | 74.7 | 71.8 | 73.7 | **76.8** |
| C2B5R3 | pp + 50 % LQR r3 | 74.0 | 37.9 | 0.41 | 73.5 | **72.6** | 73.6 | 76.3 |
C2B3R3 = best in this sweep (+0.3 over E0: within noise, needs the E7 confirmation). Stanley K12: smallest max error ever, weak circle.
**Ceiling corrected:** user asked for 80. Re-ran the perfect-driver test with the sim's own model on all 4 paths (yesterday only the
straight, the rest estimated by hand): perfect time straight 16.3, wave 16.9, lane 16.5, circle 20.1 -> average 17.5/40 ->
**best possible 77.5** (perfect tracking and stop). 80 not reachable. We are at 74.3 = 38.3 + 16.0 + 20.
Remaining: tracking ~1.7 + **time ~1.5** (circle 18.0 vs 20.1, wave 15.3 vs 16.9). Next: C3 time round (lat_accel 40-100, cruise 30).

### 2026-11-19 14:09 - Step 33: C3 results: faster curves (`2026-11-19_1409_c3_time/`); senior's note; realistic ceiling
| Config | Change | Score | Track | Time | Wave v_eq | Circle v_eq |
|---|---|---:|---:|---:|---:|---:|
| E0 | R2G10 | 74.0 | 38.0 | 16.0 | 11.5 | 13.4 |
| T40 | lat 40, cruise 30 | 74.3 | 37.9 | 16.4 | 11.7 | 14.4 |
| T60 | lat 60, cruise 30 | 74.3 | 37.9 | 16.4 | 11.6 | 14.5 |
| T100 | lat 100, cruise 30 | 74.3 | 37.9 | 16.5 | 11.7 | 14.6 |
| **T40C2** | C2 blend + lat 40, cruise 30 | **74.5** | 38.1 | 16.5 | 11.7 | 14.4 |
| T60C2 | C2 blend + lat 60, cruise 30 | 74.3 | 38.1 | 16.5 | 11.7 | 14.6 |
Faster curves work (no failures, prediction keeps it stable): time 16.0 -> 16.5. Above lat 40 stop errors grow (circle up to 5.2 m).
**New best 74.5 (T40C2).** Senior's comment (user): he also needed "path prediction" to score high, consistent with our prediction.
**Realistic ceiling** (offline, sim model, stop must be PAST the finish because stopping short lowers completion = tracking;
time from the sim's own rest rule): straight 12.07 m/s (16.1/40), circle 14.41 (19.2/40). Our circle is AT the ceiling now.
The straight (11.6) can still gain: a perfect driver brakes with a large negative command (speed loop saturated at -6 m/s^2 at once),
our profile follows a ramp. Implemented `bang_brake` (-30 until bang_release 1 m/s, then 0; trigger when remaining + aim <= v^2/(2*6)
+ 0.05 v). Offline with noise: straight v_eq 11.86, stop +2.2..2.6 m. Next: C4 sweep.

### 2026-11-19 14:20 - Step 34: C4 results: time-optimal braking (`2026-11-19_1420_c4_bang_brake/`, base T40C2)
| Config | Change | Score | Track | Time | Straight v_eq | Worst stop err |
|---|---|---:|---:|---:|---:|---:|
| T40C2 | base (ramp braking) | 74.6 | 38.2 | 16.4 | 11.5 | 4.4 |
| B1 | bang_brake | 74.5 | 37.9 | 16.6 | 11.8 | 2.3 |
| B2 | bang, aim 0.5 | 74.7 | 38.1 | 16.6 | 11.7 | 2.3 |
| B3 | bang, release 0.5 | 74.4 | 38.2 | 16.1 | 11.7 | 3.4 (wave slower: roll back) |
| B4 | bang, decel 5.8 | 74.7 | 38.0 | 16.7 | 11.7 | 2.5 |
| **B5** | bang + stop_damp 5 | **74.9** | 38.2 | **16.7** | 11.7 | 2.5 |
Full braking at the last moment gains time (16.4 -> 16.7) AND moves the stop from ~4.4 m to ~2 m past the line (much safer).
New best **74.9 (B5)**. Realistic ceiling about 77 (40 + ~17.1 + 20): left = tracking ~1.8, time ~0.4.
Next: E7 confirmation with 3 runs per path: R2G10 vs T40C2 vs B5.

### 2026-11-19 14:27 - Step 35: E7 confirmation, 3 runs per path (`2026-11-19_1427_e7_confirm/`): B5 = 74.9 confirmed
| Set | Score | Track | Time | Stop | Max err | Straight | Wave | Lane | Circle | Worst stop err |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R2G10 | 74.0 | 37.9 | 16.1 | 20.0 | 0.43 | 74.3 | 72.2 | 73.6 | 75.9 | 4.6 |
| T40C2 | 74.6 | 38.2 | 16.4 | 20.0 | 0.48 | 74.6 | 72.2 | 73.8 | 77.7 | 4.7 |
| **B5** | **74.9** | **38.3** | **16.6** | 20.0 | 0.48 | 74.8 | 72.4 | 74.3 | 77.9 | **2.5** |
36 runs, no failures. Order matches the 2-run sweeps, so the gains are real: **B5 is the new best (+0.9 over R2G10)**, and its stop
is much safer (2.5 m vs 4.6 m from the 5 m limit). Updated: demo_best.bash -> B5, START_HERE day row, MORNING_SUMMARY.
B5 = cruise 30, lat_accel 40, stop_aim 1.5, gain 0.10, predict 0.10, blend_lqr 0.3 (r 3), stop_damp 5, bang_brake.
Next: C5 tracking round around B5 (gain 0.08/0.12, predict 0.08/0.12, blend 0.2/0.4).

### 2026-11-19 14:33 - Step 36: C5 tracking round around B5 (`2026-11-19_1433_c5_tracking_b5/`): two risks found
| Config | Change | Score | Track | Note |
|---|---|---:|---:|---|
| B5 | base | 73.0 | 38.0 | **lane_change run stopped 7.2 m past the line** (stop 20 -> 7.6 on that run) |
| G08 | gain 0.08 | 74.8 | 38.3 | |
| G12 | gain 0.12 | 65.9 | 33.8 | **wave off_track after 0.88 s** (start: path heading 32 deg vs car 0 deg, full throttle) |
| P08 | predict 0.08 | 74.7 | 38.2 | |
| P12 | predict 0.12 | 74.1 | 37.5 | |
| BL2 | blend 0.2 | 74.5 | 38.1 | |
| BL4 | blend 0.4 | 74.9 | 38.3 | smallest max err 0.42 |
No clear tracking gain (all within noise); but robustness matters more: one bad run costs ~10 points.
**Investigation (14:42):** `observe_B5_lane_change` (6 runs) all fine (stop 1.8-2.2 m), so the overshoot is rare. Driver log of the bad
run: braking started ~2 m/s faster than in the good runs. Cause: the brake point is checked once per control period (20 Hz); at full
throttle the car gains ~1 m/s per period, so the decision can be one period late. Offline (40 noisy runs, sim model): 20 Hz stop
+0.2..+5.6 m (overshoots happen), deciding one tick ahead -5.5..+0.4 (short = bad for completion), **50 Hz +0.2..+3.5, 100 Hz +0.45..+2.6**.
Fix: new param `control_hz` (default 20 = old behaviour); trigger lead = one period. C6 tests 50/100 Hz with 3 runs per path.

### 2026-11-19 14:47 - Step 37: C6 results, 3 runs per path (`2026-11-19_1447_c6_control_rate/`): B6 = final best
| Config | Change | Score | Track | Time | Stop err range (12 runs) | Failures |
|---|---|---:|---:|---:|---|---|
| B5 | 20 Hz | 74.4 | 38.0 | 16.4 | 0.90-3.69 m | none |
| H50 | 50 Hz | 74.7 | 38.1 | 16.6 | 0.34-2.87 m | none |
| H100 | 100 Hz | 74.7 | 38.1 | 16.6 | 1.05-3.14 m | none |
| **H100G09 = B6** | 100 Hz + gain 0.09 | **74.9** | 38.3 | 16.6 | 1.14-2.92 m | none |
**B6 = B5 + control_hz 100 + lookahead_gain 0.09: 74.9 with every stop safely inside the zone** (48 runs, no failures).
Faster control also helps slightly overall (+0.3). demo_best.bash, START_HERE, MORNING_SUMMARY, NEXT_SESSION updated to B6.
Status vs ceiling: 74.9 = tracking 38.3 + time 16.6 + stop 20 against about 77 (40 + ~17.1 + 20).

### 2026-11-19 ~15:05 - Step 38: Best-score snapshot; which paper methods are tested; C7 real steering model
**Snapshot:** `BEST_SCORES.md` (every best set: score, all parameters, results folder, how to rerun), frozen script
`_SCRIPT/2026-11-19_script/run_best_B6_74.9.bash`, git tags `best-B6-74.9` and `best-N-70.3` (pushed).
**Tested so far:** pure pursuit, Stanley, predictive Stanley, feed-forward (enhanced Stanley, pp + ff), kinematic MPC as LQR (+ blend),
time-optimal speed profile / braking. **Not yet:** learning the model error (MAP2 / FS 2026), system identification (RA-L 2025),
RL lookahead (RA-L 2026), constrained MPC. Not applicable: tyre/friction papers (LLA-MPC, tyre sys-ID).
**Chosen next (user: "the one that helps"):** predict with the simulator's real steering loop. Our prediction used a first-order lag
(0.10 s); the sim uses a PI loop with zeta 0.28 (overshoots). New `steer_model pi`: roll() runs the same PI law
(rate = clamp(kp e + ki int e, +-1 rad/s), anti-windup), and the driver keeps its own copy of the PI integral, updated every tick from
command vs actual steering. C7 sweep: B6 vs pi model with predict 0.08/0.10/0.12/0.15 and gain 0.10.
