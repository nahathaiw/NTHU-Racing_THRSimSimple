# Morning summary (updated after every experiment)

**Last update:** 2026-11-19 ~02:46, after E3/E4.  **Best so far: R2G10 = pure pursuit + prediction (74.2 twice; 73.6-74.0 in
later same-session checks; noise between sweeps about 0.6).** Ceiling with official settings about 76.

| ID | Method (paper) | Best score | vs same-session R2G10 | Verdict |
|---|---|---:|---:|---|
| E1 | Stanley (Hoffmann 2007, DLR 2026) | 73.0 | 73.6 | needs prediction; ~0.6 below |
| E2 | Predictive Stanley (DLR 2026) | 72.8 | 74.0 | worse than plain Stanley here |
| E3 | Rear-axle Stanley + feed-forward (DLR 2026) | 73.5 | 73.9 | best Stanley, within noise, not better |
| E4 | Pure pursuit + feed-forward (Kapania & Gerdes 2015) | 73.5 | 73.9 | no gain; more ff = worse wave |
| E5 | Kinematic MPC / LQR with steering lag (MAP2, LPV-MPC, FS 2026) | running | | |

Details: `personal_log.md` (one step per experiment), `experiment_plan.md` (table), results in `_RESULTS/2026-11-19_eval-result/`.
