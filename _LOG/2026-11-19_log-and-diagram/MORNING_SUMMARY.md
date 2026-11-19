# Morning summary (updated after every experiment)

**Last update:** 2026-11-19 ~14:10, after C1/C2. **Ceiling corrected to 77.5** (perfect driver on all 4 paths with the sim's own model; time max 17.5/40). 80/90 not reachable with official settings.
later same-session checks; noise between sweeps about 0.6).** Ceiling with official settings about 76.

| ID | Method (paper) | Best score | vs same-session R2G10 | Verdict |
|---|---|---:|---:|---|
| E1 | Stanley (Hoffmann 2007, DLR 2026) | 73.0 | 73.6 | needs prediction; ~0.6 below |
| E2 | Predictive Stanley (DLR 2026) | 72.8 | 74.0 | worse than plain Stanley here |
| E3 | Rear-axle Stanley + feed-forward (DLR 2026) | 73.5 | 73.9 | best Stanley, within noise, not better |
| E4 | Pure pursuit + feed-forward (Kapania & Gerdes 2015) | 73.5 | 73.9 | no gain; more ff = worse wave |
| E5 | Kinematic MPC / LQR with steering lag (MAP2, LPV-MPC, FS 2026) | 73.2 | 74.4 | lower r better (r30 > r100 > r300): tune further (E6, r 3-10) |

Details: `personal_log.md` (one step per experiment), `experiment_plan.md` (table), results in `_RESULTS/2026-11-19_eval-result/`.
| E6 | LQR tuning | 73.7 (r20) | 73.9 | best r 20-30; strong LQR (r3) best wave |
| C1 | Stanley K8/K12 | 73.7 (K12) | 74.0 | smallest max error 0.35 m, weak on circle |
| C2 | Pure pursuit + 30 % LQR (r3) | **74.3** | 74.0 | best so far in-session (+0.3, within noise) |
| C3 | Time round: lat_accel 40-100, cruise 30 | running | | |
