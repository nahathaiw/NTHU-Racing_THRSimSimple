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
