#!/usr/bin/env bash
# Parameter sweep, round 2 (around the best set G): for each config start my_driver with those ROS parameters,
# run a headless evaluation, stop the driver, print + save a one-line summary.
#
# Usage:  "./11.18.26 script/sweep.bash" [-n RUNS_PER_PATH]      (default 2)
# Output: eval_results/sweep/<name>.json  and  eval_results/sweep/summary.txt
# Needs the workspace built (colcon build) and NO other driver running.
set -u
pkill -f "lib/my_driver/driver" 2>/dev/null
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNS=2
[ "${1:-}" = "-n" ] && RUNS="$2"

# system tools first: Anaconda's python breaks ROS
export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"
set +u   # ROS setup files read unset variables
source /opt/ros/humble/setup.bash
source "$WS/install/setup.bash"
set -u

OUT="$WS/eval_results/sweep2"
mkdir -p "$OUT"
: > "$OUT/summary.txt"

# name  then  ROS parameters (defaults: cruise 12, lat 3.0, brake 3.5, aim 1.5)
CONFIGS=(
  "H  cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.5 stop_aim:=3.0 lookahead_gain:=0.25"
  "I  cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.5 stop_aim:=3.0 lookahead_gain:=0.15"
  "J  cruise_speed:=25.0 lat_accel:=7.0 brake_decel:=5.5 stop_aim:=3.0 lookahead_gain:=0.25"
  "K  cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.8 stop_aim:=3.0 lookahead_gain:=0.25"
  "L  cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.5 stop_aim:=3.0 lookahead_gain:=0.25 lookahead_base:=2.0"
  "H2 cruise_speed:=25.0 lat_accel:=6.0 brake_decel:=5.5 stop_aim:=3.0 lookahead_gain:=0.25"
)

for cfg in "${CONFIGS[@]}"; do
  name="${cfg%% *}"
  params="${cfg#* }"
  args=()
  for p in $params; do args+=(-p "$p"); done

  echo ">>> [$name] $params"
  ros2 run my_driver driver --ros-args "${args[@]}" > "$OUT/$name.driver.log" 2>&1 &
  sleep 2
  "$WS/evaluate.bash" --headless -n "$RUNS" -o "$OUT/$name.json" > "$OUT/$name.sim.log" 2>&1
  pkill -INT -f "lib/my_driver/driver" 2>/dev/null
  sleep 1

  /usr/bin/python3 - "$OUT/$name.json" "$name" "$params" <<'PY' | tee -a "$OUT/summary.txt"
import json, sys
f, name, params = sys.argv[1:4]
try:
    d = json.load(open(f))
except Exception as e:
    print(f"[{name}] {params}\n   NO RESULT ({e}); see the .sim.log / .driver.log files")
    sys.exit()
runs = d["runs"]
n = len(runs) or 1
trk = sum(r["tracking"] for r in runs) / n * 0.4
tim = sum(r["time_score"] for r in runs) / n * 0.4
stp = sum(r["stop"] for r in runs) / n * 0.2
bad = [f'{r["shape"]}:{r["result"]}' for r in runs if r["result"] != "stopped"]
worst = max(r["max_cte"] for r in runs)
print(f"[{name}] {params}")
print(f"   OVERALL {d['overall_score']:.1f} = track {trk:.1f} + time {tim:.1f} + stop {stp:.1f}"
      f" | max_cte {worst:.2f} m | failures: {', '.join(bad) if bad else 'none'}")
print("   per path: " + "  ".join(f"{k} {v['score']:.1f} (v_eq {v['v_eq']:.1f})" for k, v in d["per_path"].items()))
PY
done
echo "Done. Summary: $OUT/summary.txt"
