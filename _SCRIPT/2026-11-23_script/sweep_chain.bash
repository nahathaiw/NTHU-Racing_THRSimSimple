#!/usr/bin/env bash
# 2026-11-23 sweep for the full chain: cones -> FSGPathPlan (cone_planner_node.py) -> my_driver -> simulator.
# Each config = set N base + the overrides on its line (same base as 2026-11-19 sweep.bash).
#   name:=value      driver parameter
#   pl.name:=value   planner option (--name value): range, fov, width, spacing, noise, rate, steps, min_travel
#   chain:=off       no planner: the driver gets the TRUE path (baseline, same session)
# With the chain on, the driver runs with `-r /path:=/planned_path -p replan:=true`.
#
# Usage:  ./_SCRIPT/2026-11-23_script/sweep_chain.bash SWEEP_NAME CONFIG_FILE [-n RUNS_PER_PATH]   (default 2)
# Output: _RESULTS/2026-11-23_eval-result/<YYYY-MM-DD_HHMM>_<SWEEP_NAME>/<YYYY-MM-DD_HHMM>_<ID>/
#           eval.json eval.png driver.log planner.log sim.log params.txt ; summary.txt
set -u
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWEEP="$1"; CFG="$2"; RUNS=2
[ "${3:-}" = "-n" ] && RUNS="$4"
PAT="[l]ib/my_driver/driver|[t]hr_sim/lib/thr_sim|[r]un_sim.bash|[e]valuate.bash|[d]emo_best|[c]one_planner_node"
busy() { pgrep -f "$PAT" > /dev/null; }
if busy; then
  echo "ABORT: another driver/simulator/planner is running. Close it first:"; pgrep -af "$PAT" | cut -c1-120
  exit 1
fi

export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"
set +u; source /opt/ros/humble/setup.bash; source "$WS/install/setup.bash"; set -u

OUT="$WS/_RESULTS/2026-11-23_eval-result/$(date +%Y-%m-%d_%H%M)_$SWEEP"
mkdir -p "$OUT"; cp "$CFG" "$OUT/configs.txt"; : > "$OUT/summary.txt"
BASE="cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.9 stop_aim:=2.0 lookahead_gain:=0.25"

grep -v '^\s*#' "$CFG" | grep -v '^\s*$' | while read -r id over; do
  for _ in 1 2 3 4 5 6 7 8 9 10; do busy || break; sleep 1; done
  if busy; then echo "ABORT before [$id]: something else is running" | tee -a "$OUT/summary.txt"; exit 1; fi
  D="$OUT/$(date +%Y-%m-%d_%H%M)_$id"; mkdir -p "$D"
  args=(); pl=(); chain=1
  for p in $BASE $over; do
    case "$p" in
      chain:=off) chain=0 ;;
      pl.*) k="${p#pl.}"; pl+=("--${k%%:=*}" "${k#*:=}") ;;
      *) args+=(-p "$p") ;;
    esac
  done
  echo "$BASE $over" > "$D/params.txt"
  echo ">>> [$id] $over"
  if [ "$chain" = 1 ]; then
    python3 "$HERE/cone_planner_node.py" "${pl[@]}" > "$D/planner.log" 2>&1 &
    ros2 run my_driver driver --ros-args -r /path:=/planned_path -p replan:=true "${args[@]}" > "$D/driver.log" 2>&1 &
  else
    ros2 run my_driver driver --ros-args "${args[@]}" > "$D/driver.log" 2>&1 &
  fi
  sleep 3
  "$WS/evaluate.bash" --headless -n "$RUNS" -o "$D/eval.json" > "$D/sim.log" 2>&1 < /dev/null
  pkill -INT -f "lib/my_driver/driver" 2>/dev/null; pkill -INT -f "[c]one_planner_node" 2>/dev/null; sleep 1
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
print("   rms err [cm]: " + "  ".join(f"{x['shape'][:4]} {100*x['rms_cte']:.0f}" for x in r))
PY
done
echo "summary: $OUT/summary.txt"
