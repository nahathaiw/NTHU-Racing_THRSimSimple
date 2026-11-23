# Personal log 2026-11-23: FSGPathPlan

### 2026-11-23 18:50 - Step 1: What FSGPathPlan is
Source: github.com/weichang0307/FSGPathPlan (commit 79c1b7f), cloned OUTSIDE this repo to `~/Desktop/pleng/FSGPathPlan`
(not ours; not committed here). Runs with the conda env `dev_py` (system python has no pandas / no venv).
- **Input:** cones (blue = left, yellow = right), like a camera/lidar sees on a real FS track. **Output:** predicted centre line, 60 m ahead.
- **Planner** (`Path_planer.py`, `Yaw_optimizer.py`): 40 steps of 1.5 m. Each step's heading = gradient ascent on
  prior (exp(-3 (yaw - car_yaw)^2): do not turn sharply) x likelihood (keep MARGIN 2.5 m from blue on the left and yellow on the
  right, nearer cones weigh more: exp(-1.2 dist)). Heading change at most 0.4 rad per step. Also a confidence per step.
- **Smoother** (`Path_smoother.py`): force model; cones within 1.5 m push the point away, neighbours pull it in line (20 iterations).
- **Meaning for us:** this is "path prediction" = predicting WHERE THE TRACK GOES from cones. On the real car no path is given, so this
  comes BEFORE our driver. In THRSim the path is given on /path and the score measures error to that exact path, so FSGPathPlan cannot
  raise the THRSim score; it is the next piece for the real car.

### 2026-11-23 18:56 - Step 2: How accurate is it? (`_RESULTS/2026-11-23_eval-result/2026-11-23_1856_fsg_try/`)
Script `_SCRIPT/2026-11-23_script/fsg_try.py`. Error = distance of each predicted point to the true centre line.
| Track | Raw plan mean / max [m] | Smoothed mean / max [m] | Plan + smooth time |
|---|---|---|---|
| FSG random track seed 0-3 (width 5, cones 4 m) | 0.09-0.18 / 0.30-0.64 | 0.13-0.23 / 0.27-0.73 | 7-9 + 80-90 ms |
| THRSim straight (as cones, width 5, every 4 m) | 0.00 / 0.00 | 0.00 / 0.00 | 5 + 18 ms |
| THRSim wave | 0.11 / 0.20 | 0.16 / 0.30 | 4 + 18 ms |
| THRSim lane_change | 0.04 / 0.14 | 0.05 / 0.19 | 5 + 18 ms |
| THRSim circle (60 m = 2/3 of the loop) | 0.12 / 0.17 | 0.29 / 0.47 | 6 + 25 ms |
**Findings:** (1) the planner finds the centre line well, about 0.1 m mean error, every plan. (2) The smoother makes it WORSE in curves
(circle 0.12 -> 0.29 m): the neighbour pull cuts corners (pulls the line inward). (3) Fast enough: planner 5-9 ms; the smoother is the
slow part (pure Python, every point x every cone). (4) The "confidence" is a product of 40 step probabilities, so it shrinks to
1e-6..1e-14: only useful relative, not as a probability. (5) MARGIN 2.5 m assumes a 5 m track; FSG minimum is 3 m, so on narrow tracks
MARGIN must be set to half the width.
Plots: `fsg_tracks.png` (random FSG tracks), `thrsim_paths.png` (our 4 paths as cones).

### 2026-11-23 ~19:00 - Step 3: Plan A, the full chain in the simulator
User chose A. Chain: simulator `/path` (true) -> `cone_planner_node.py` (makes cones, gives FSGPathPlan only the cones the car SEES:
within `range` 15 m and +-50 deg, re-plans at 10 Hz from the car pose, spline-resampled to 0.5 m) -> `/planned_path` -> our driver
(`-r /path:=/planned_path -p replan:=true`, never sees the true path) -> car. The scorer still uses the TRUE path.
- Driver: new param `replan` (default false): a new path every 0.1 s must not clear the braking latch (and no ILC).
- Planner MARGIN = width/2 (FSGPathPlan's 2.5 m fits our 5 m cone track). Planning time about 3.5 ms.
- Runner: `_SCRIPT/2026-11-23_script/sweep_chain.bash` (`pl.x:=v` = planner option, `chain:=off` = true-path baseline).

### 2026-11-23 19:05 - Step 4: smoke test + A1 (`2026-11-23_1905_a0_smoke/`, `2026-11-23_1907_a1_chain/`)
**Steering through the chain works:** RMS sideways error 5-17 cm, close to the true-path runs (2-14 cm); max 0.3-0.4 m.
**Stopping failed** (overrun or 18 m past): the finish was only taken after 20 m of driving (circle guard), when the car was already at
23 m/s and ~25 m before the line (needs ~45 m). Also a bug: 15 m past the finish it was "forgotten" and the car drove on.
Only FR15C14 (finish seen at 15 m, top speed 14 m/s) stopped every time: **72.2** vs TRUE 75.2.
**Fixes:** "passed" latches until the next run (and needs the finish within 5 m); the finish is known as soon as it is > 2 m in front
and within `finish_range`, matched to the nearest planned point within 10 m (beyond the seen cones the plan is a straight guess);
a teleport back to the start is not counted as driven distance. A1 stop results are invalid (bug); A2 = rerun.
Lesson: with cones seen only 15 m ahead, the car may only go as fast as it can stop in what it sees: v <= sqrt(2 * 6 * 15) = 13.4 m/s.

### 2026-11-23 19:20 - Step 5: A2 after the finish fix (`2026-11-23_..._a2_chain_fixed/`, 2 runs/path)
TRUE 75.2 | FR60 68.8 (circle stops 16 m late) | FR30 50.4 (overrun: finish seen at 30 m, car too fast to stop) | FR15C14 72.2 |
**R30FR60 74.5** | N10FR60 68.7 (circle 13 m late). Straight / wave / lane change now stop at the line.
Circle cause: beyond the seen cones the plan is a straight guess, so it only passes near the finish when the car is close.

### 2026-11-23 19:35 - Step 6: A3 circle fix (`2026-11-23_..._a3_circle_fix/`, 2 runs/path)
Fix: if the finish is known but the plan does not reach it (< 3 m), put the finish at the STRAIGHT-LINE distance (never longer than
the real distance along the track, so the car brakes a little early, never late).
| Config | Score | Failures | Circle |
|---|---:|---|---:|
| TRUE (POL, true path) | 75.5 | none | 78.2 |
| **FR60** (cones 15 m, finish known) | **74.3** | none | 76.3 (was 54.6) |
| R30FR60 (cones 30 m) | 74.3 | none | 75.8 |
| N10FR60 (+10 cm cone noise) | 74.2 | none | 76.0 |
**The full chain works: cones -> FSGPathPlan -> POL = 74.3, only 1.2 below driving on the true path.** Cone noise of 10 cm costs ~0.1.
What is lost: wave 74.2 -> 71.7 (plan error ~15 cm) and circle 78.2 -> 76.3 (slower: v_eq 14.5 -> 14.0, plan only sees 15 m).

### 2026-11-23 19:40 - Step 7: Task 1 safe speed + task 2 wave gap, B1 (`..._b1_safe_and_wave/` stopped, rest in `2026-11-23_1952_b1b_rest/`)
New: driver `sight_dist` (speed <= sqrt(2 * 6 * sight)); planner `--memory` (cone map), `--step`, `--blend` (mix with previous plan).
First try hung ~10 min: `sight_dist:=15` is an integer and the driver (double param) crashed at start; the simulator waited forever.
Folder labelled `_INVALID-driver-crash-int-param`; ALWAYS write ROS double params with a dot (15.0). Added a crash guard to sweep_chain.bash.
| Config | Score | Note |
|---|---:|---|
| TRUE | 75.2 (75.4 in b1) | true path |
| FR60 (b1) | 74.5 | chain reference |
| **SAFE15** (15 m sight, automatic speed) | **72.1** | = hand-set FR15C14 72.2: the automatic rule works (v_eq 10) |
| SAFE30 | 68.4 | circle stopped 12 m SHORT (see below) |
| MEM (cone memory) | 74.1 | no help |
| STEP1 (1.0 m steps) | 74.6 | +0.1, noise |
| BL5 / MEMBL5 (blend 0.5) | 67.5 / 69.6 | worse: plan lags behind, circle stop late/short |
**Two causes found:** (1) circle, 30 m sight: the finish is "known" from across the circle; straight-line 30 m vs ~47 m along the
track; the car brakes far too early and the brake latch cannot let go -> 12 m short. (2) wave gap: every plan starts AT the car, so
the plan carries the car's own sideways error (wave 13-15 cm vs 7 cm on the true path); the driver follows the plan, not the centre.
**Fixes (B2):** driver: with `replan`, the brake latch releases if the finish is > 5 m farther than the stopping distance.
Planner `--center 1`: start the plan at the estimated track centre beside the car (midpoint of the nearest blue and yellow cone).

### 2026-11-23 20:02 - Step 8: B2 first try INVALID (`..._b2_center_unlatch_INVALID-finish-gap-bug/`)
Every chain config stopped 10-15 m off (TRUE fine, 75.4). Cause: with the new brake release, a hidden planner gap showed up: in the
last 2 m the finish is no longer "> 2 m in front" but not "passed" yet, so the planner said "finish unknown" = path end 60 m away,
and the brake let go. The old brake latch had hidden this. Fix: once seen, the finish stays known until passed (`fin_known`).

### 2026-11-23 20:12 - Step 9: B2 rerun (`2026-11-23_2012_b2_center_unlatch/`, 2 runs/path)
| Config | Score | Circle | Wave | Note |
|---|---:|---:|---:|---|
| TRUE | 75.4 | 78.1 | 74.0 | true path |
| FR60 (cones 15 m, finish known) | 73.8 | 74.9 | 72.1 | (74.3-74.5 before; ~noise / brake release) |
| CEN (plan from track centre) | 72.8 | 71.0 | 71.7 | WORSE (circle error up to 38 cm) |
| CENS1 (centre + 1 m steps) | 73.3 | 71.6 | 72.3 | worse |
| **SAFE15** (15 m sight, automatic speed) | **72.1** | 72.9 | 70.7 | same as B1: automatic speed rule works |
| **SAFE30** (30 m sight, automatic speed) | **73.8** | 74.4 | 72.6 | **fixed** (was 68.4, circle 12 m short) |
| SAFE30C (+ centre) | 73.0 | 72.6 | 71.5 | worse |
**Task 1 done:** the car sets its own safe speed from its sight distance and stops correctly on every path:
15 m sight (camera) 72.1, 30 m sight (lidar) 73.8, vs 75.4 on the true path.
**Task 2 not solved:** the centre start made it worse. The midpoint of the nearest blue and nearest yellow cone is not a good centre
estimate (they are usually not a pair; in curves the inner and outer cones are at different places along the track), so it adds
noise. Cone memory, 1 m steps and blending did not help either. The wave gap (~2 points, plan error 14-18 cm vs 7 cm) comes from
FSGPathPlan itself (offline error on the wave 0.11 m mean, step 2). Closing it needs a better planner (e.g. fit the centre line
through cone-pair midpoints), not more tuning around it.
