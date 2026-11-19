#!/usr/bin/env bash
# Record several runs of ONE path with set B5 (+ overrides) to study rare problems.
# Usage: ./_SCRIPT/2026-11-19_script/observe_shape.bash NAME SHAPE RUNS [name:=value ...]
set -u
WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="$1"; SHAPE="$2"; RUNS="$3"; shift 3
if pgrep -f "[l]ib/my_driver/driver|[t]hr_sim/lib/thr_sim|[r]un_sim.bash|[e]valuate.bash|[d]emo_best" > /dev/null; then echo "ABORT: something else is running"; exit 1; fi
export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v anaconda | paste -sd:)"
set +u; source /opt/ros/humble/setup.bash; source "$WS/install/setup.bash"; set -u
OUT="$WS/_RESULTS/2026-11-19_eval-result/$(date +%Y-%m-%d_%H%M)_observe_${NAME}_${SHAPE}"; mkdir -p "$OUT"
P=(cruise_speed:=30.0 lat_accel:=40.0 brake_decel:=5.9 stop_aim:=1.5 lookahead_gain:=0.10 predict_time:=0.10 blend_lqr:=0.3 lqr_r:=3.0 ff_time:=0.10 stop_damp:=5.0 bang_brake:=true "$@")
A=(); for p in "${P[@]}"; do A+=(-p "$p"); done; echo "${P[*]}" > "$OUT/params.txt"
ros2 run my_driver driver --ros-args "${A[@]}" > "$OUT/driver.log" 2>&1 &
/usr/bin/python3 "$HERE/record_run.py" "$OUT" > "$OUT/recorder.log" 2>&1 & REC=$!
sleep 2
"$WS/evaluate.bash" --headless -n "$RUNS" -s "$SHAPE" -o "$OUT/eval.json" > "$OUT/sim.log" 2>&1 < /dev/null
sleep 1; kill -INT $REC; pkill -INT -f "lib/my_driver/driver"; sleep 1
echo "$OUT"; cat "$OUT/delays.txt"
