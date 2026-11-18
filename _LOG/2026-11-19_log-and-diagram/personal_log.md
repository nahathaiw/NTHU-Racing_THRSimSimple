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
