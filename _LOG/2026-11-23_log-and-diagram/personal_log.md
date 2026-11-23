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
