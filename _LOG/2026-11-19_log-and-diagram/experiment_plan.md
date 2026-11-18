# Experiment plan: new steering methods from 2025-2026 papers

Goal: beat **R2G10 = 74.2** (ceiling about 76). Time (16/40) and stop (20/20) are already maxed, so every experiment is about
**tracking** (38.2/40, RMS path error). Speed profile, prediction, stop_damp stay as in R2G10 unless the row says otherwise.
Each experiment: 2 runs per path (8 runs), same sweep script, results in `_RESULTS/2026-11-19_eval-result/`.
Status: TODO -> RUNNING -> DONE (or FAILED / SKIPPED). Filled in step by step; details of each step in `personal_log.md`.

## The list

| ID | Method | From paper | What changes in the driver | Why it might help |
|---|---|---|---|---|
| E0 | **Baseline R2G10** (pure pursuit + prediction) | our work today | nothing | reference to beat |
| E1 | Stanley | Hoffmann et al. 2007; DLR 2026 (base Stanley) | steering = heading error + atan(k * cross-track error / v), front axle | different steering law; often tracks tighter than pure pursuit |
| E2 | Predictive Stanley | DLR 2026 (best RMSE in their sim) | E1, but computed from the **predicted** pose | Stanley + our latency fix |
| E3 | Predictive Stanley + feed-forward | DLR 2026 (enhanced Stanley); Kapania & Gerdes 2015 | E2 + steering the path curvature needs, atan(L * kappa) | feedback only corrects small errors, less weaving |
| E4 | Pure pursuit + curvature feed-forward | Kapania & Gerdes 2015 | R2G10 + feed-forward term, blended | same idea on our current controller |
| E5 | Kinematic MPC with steering lag (LQR form) | MAP2 2026; LPV-MPC 2026; FS Driverless 2026 | new steering mode: linear model of path error + steering lag, optimal gains over a horizon (finite-horizon Riccati, no solver library) | the "full" version of prediction: plans many steps, knows the wheel lags |
| E6 | E5 with tuned weights | same | sweep error vs steering-effort weights, horizon | find the best MPC setting |
| E7 | Best of E1-E6 + confirmation | | 3 runs per path (12 runs), official style | a reliable final number |
| E8 | (optional) RL-tuned lookahead | RL pure pursuit, RA-L 2026 | policy picks lookahead and gain from speed + curvature | learning project; needs a training loop |

## Results (filled in as we go)

| ID | Status | Date-time | Score | Track /40 | Time /40 | Stop /20 | Max err (m) | Failures | Result folder | Note |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| E0 | DONE | 2026-11-19 01:4x / 01:52 | 74.2 | 38.2 | 16.0 | 20.0 | 0.56 / 0.51 | none | `..._p6_tracking/..._R2G10`, `..._p7_short_lookahead/..._S0` | scored 74.2 twice |
| E1 | DONE | 2026-11-19 02:21 | 73.0 (best: K4) | 36.9 | 16.1 | 20.0 | 0.51 | none (paper version without prediction: 3 off-track) | `2026-11-19_0221_e1_stanley/` | same-session E0 = 73.6. Stanley is ~0.6 below pure pursuit; needs prediction; higher K better (K1 71.5, K2 72.6, K4 73.0); yaw damping no help (72.4) |
| E2 | RUNNING | 2026-11-19 ~02:32 | | | | | | | `..._e2_predictive_stanley/` | predictive Stanley N 3/6, decay 0.5/0.7, K4/K6 |
| E3 | TODO | | | | | | | | | |
| E4 | TODO | | | | | | | | | |
| E5 | TODO | | | | | | | | | |
| E6 | TODO | | | | | | | | | |
| E7 | TODO | | | | | | | | | |
| E8 | optional | | | | | | | | | |
