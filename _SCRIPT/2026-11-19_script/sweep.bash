#!/usr/bin/env bash
# Sweep for 2026-11-19. Each config = set N + the overrides on its line.
#
# Usage:  ./_SCRIPT/2026-11-19_script/sweep.bash SWEEP_NAME CONFIG_FILE [-n RUNS_PER_PATH]   (default 2)
# CONFIG_FILE: one config per line,  ID  name:=value name:=value ...   (# = comment)
# Output: _RESULTS/2026-11-19_eval-result/<YYYY-MM-DD_HHMM>_<SWEEP_NAME>/
#           <YYYY-MM-DD_HHMM>_<ID>/ eval.json eval.png driver.log sim.log params.txt
#           summary.txt  (one block per config)
set -u
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SWEEP="$1"; CFG="$2"; RUNS=2
[ "${3:-}" = "-n" ] && RUNS="$4"
# Guard: another driver or simulator (GUI demo, other sweep) would fight over the car and spoil every result.
busy() { pgrep -f "[l]ib/my_driver/driver|[t]hr_sim/lib/thr_sim|[r]un_sim.bash|[e]valuate.bash|[d]emo_best" > /dev/null; }
if busy; then
  echo "ABORT: another driver/simulator is running. Close it first:"; pgrep -af "[l]ib/my_driver/driver|[t]hr_sim/lib/thr_sim|[r]un_sim.bash|[e]valuate.bash|[d]emo_best" | cut -c1-120
  exit 1
fi

export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"
set +u; source /opt/ros/humble/setup.bash; source "$WS/install/setup.bash"; set -u

OUT="$WS/_RESULTS/2026-11-19_eval-result/$(date +%Y-%m-%d_%H%M)_$SWEEP"
mkdir -p "$OUT"; cp "$CFG" "$OUT/configs.txt"; : > "$OUT/summary.txt"
BASE="cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.9 stop_aim:=2.0 lookahead_gain:=0.25"

grep -v '^\s*#' "$CFG" | grep -v '^\s*$' | while read -r id over; do
  for _ in 1 2 3 4 5 6 7 8 9 10; do busy || break; sleep 1; done   # let the last run shut down
  if busy; then echo "ABORT before [$id]: something else is running (see above)" | tee -a "$OUT/summary.txt"; exit 1; fi
  D="$OUT/$(date +%Y-%m-%d_%H%M)_$id"; mkdir -p "$D"
  args=(); for p in $BASE $over; do args+=(-p "$p"); done   # later values win
  echo "$BASE $over" > "$D/params.txt"
  echo ">>> [$id] $over"
  ros2 run my_driver driver --ros-args "${args[@]}" > "$D/driver.log" 2>&1 &
  sleep 2
  "$WS/evaluate.bash" --headless -n "$RUNS" -o "$D/eval.json" > "$D/sim.log" 2>&1 < /dev/null
  pkill -INT -f "lib/my_driver/driver" 2>/dev/null; sleep 1
  /usr/bin/python3 - "$D/eval.json" "$id" "$over" <<'PY' | tee -a "$OUT/summary.txt"
import json, sys
f, name, over = sys.argv[1:4]
try:
    d = json.load(open(f))
except Exception as e:
    print(f"[{name}] {over}\n   NO RESULT ({e})"); sys.exit()
r = d["runs"]; n = len(r) or 1
trk = sum(x["tracking"] for x in r) / n * 0.4; tim = sum(x["time_score"] for x in r) / n * 0.4
stp = sum(x["stop"] for x in r) / n * 0.2
bad = [f'{x["shape"]}:{x["result"]}' for x in r if x["result"] != "stopped"]
print(f"[{name}] {over}")
print(f"   OVERALL {d['overall_score']:.1f} = track {trk:.1f} + time {tim:.1f} + stop {stp:.1f} | max_cte {max(x['max_cte'] for x in r):.2f} m | failures: {', '.join(bad) or 'none'}")
print("   per path: " + "  ".join(f"{k} {v['score']:.1f} (v_eq {v['v_eq'] or 0:.1f}, err {v['mean_abs_stop_err'] or 0:.1f})" for k, v in d["per_path"].items()))
PY
done
echo "summary: $OUT/summary.txt"
