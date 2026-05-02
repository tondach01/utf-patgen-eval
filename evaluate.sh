#!/bin/bash

# evaluate.sh - Evaluate hyph-bench datasets against different patgen binaries and profiles in parallel.
# Measures execution time using /usr/bin/time -v, and true physical memory using systemd cgroups.
#
# Usage: Run from the project root on Linux.
# ./scripts/evaluate.sh [output.csv]

# Pre-flight check for systemd
if ! systemctl --user is-system-running &>/dev/null && [ "$(systemctl --user is-system-running 2>/dev/null)" != "degraded" ]; then
    echo "ERROR: systemd user instance is not running."
    echo "In WSL, ensure you have systemd enabled in /etc/wsl.conf:"
    echo -e "[boot]\nsystemd=true"
    echo "Then restart WSL using 'wsl --shutdown' from PowerShell."
    exit 1
fi

BINARIES=("/packages/run.64/texlive-2025/bin/patgen" "../utf-patgen/build/utfpatgen")
PROFILES_DIR=${PROFILES_DIR:-profiles}
DATA_DIR=${DATA_DIR:-data}
OUTPUT_FILE=${1:-evaluation_results.csv}
JOBS=${JOBS:-$(nproc 2>/dev/null || echo 1)}
ITERATIONS=${ITERATIONS:-1}
LOGS_DIR=${LOGS_DIR:-logs}

mkdir -p "$LOGS_DIR"

WLH_FILES=$(find "$DATA_DIR" -name "*.wlh" | sort)

evaluate_task() {
    local iteration="$1"
    local binary="$2"
    local profile="$3"
    local wlh="$4"
    local output_file="$5"
    local wlh_conv=""
    
    local profile_name=$(basename "$profile")
    local dataset_name=$(basename "$wlh" .wlh)
    local binary_name=$(basename "$binary")
    local tr="${wlh%.wlh}.tr"
    
    if [ ! -f "$tr" ]; then
        return
    fi

    local abs_binary
    if command -v "$binary" >/dev/null 2>&1; then
        abs_binary=$(command -v "$binary")
    else
        abs_binary=$(realpath "$binary")
    fi
    local abs_wlh=$(realpath "$wlh")
    local abs_tr=$(realpath "$tr")

    local tmp_dir=$(mktemp -d -p "$PWD" tmp_eval_XXXXXX)
    local input_file="$tmp_dir/input.in"
    
    if [[ "$binary_name" != "patgen" ]]; then
        wlh_conv=${tmp_dir}/dict.wlh
        sed -b 's/1/\xFE\x01/g; s/2/\xFE\x02/g; s/3/\xFE\x03/g; s/4/\xFE\x04/g; s/5/\xFE\x05/g; s/6/\xFE\x06/g; s/7/\xFE\x07/g; s/8/\xFE\x08/g; s/9/\xFE\x09/g' "$abs_wlh" > "$wlh_conv"
        abs_wlh="$wlh_conv"
    fi

    local task_log="$LOGS_DIR/${dataset_name}_${binary_name}_${profile_name}_${iteration}.log"
    echo "[STARTED]  $dataset_name | $binary_name | $profile_name | $iteration/$ITERATIONS"
    
    local num_levels=$(grep -v '^#' "$profile" | grep -v '^[[:space:]]*$' | wc -l)
    echo "1 $num_levels" > "$input_file" 
    while read -r line; do
        [[ "$line" =~ ^# ]] && continue
        [[ -z "$line" ]] && continue
        
        if [[ "$line" =~ ([0-9]+[[:space:]]+){4}[0-9]+ ]]; then
            read -r p_s p_f g b t <<< "$line"
            echo -e "${p_s} ${p_f}\n${g} ${b} ${t}" >> "$input_file"
        fi
    done < "$profile"
    echo "y" >> "$input_file"
    
    local run_id="eval_$(tr -dc a-z0-9 </dev/urandom | head -c 6)_$$"
    local wrapper_script="$tmp_dir/run_${run_id}.sh"

    cat <<EOF > "$wrapper_script"
#!/bin/bash
/usr/bin/time -v "$abs_binary" "$abs_wlh" /dev/null "$tmp_dir/final.pat" "$abs_tr" < "$input_file" > "$task_log" 2> "$tmp_dir/time.log"
systemctl --user show "$run_id" --property=MemoryPeak | cut -d= -f2 > "$tmp_dir/memory_peak.log"
EOF

    chmod u+x "$wrapper_script"
    systemd-run --user --wait -q -d -p MemoryAccounting=yes --unit="$run_id" "$wrapper_script"
    
    local user_time=$(grep "User time (seconds):" "$tmp_dir/time.log" | awk '{print $4}')
    
    local memory_peak_bytes=0
    if [ -f "$tmp_dir/memory_peak.log" ]; then
        memory_peak_bytes=$(cat "$tmp_dir/memory_peak.log")
    fi
    
    local memory_peak=0
    if [[ "$memory_peak_bytes" =~ ^[0-9]+$ ]]; then
        memory_peak=$((memory_peak_bytes / 1024))
    else
        echo "[WARNING] MemoryPeak not recorded for $run_id. Falling back to time -v RSS."
        memory_peak=$(grep "Maximum resident set size (kbytes):" "$tmp_dir/time.log" | awk '{print $6}')
    fi

    local last_stats=$(grep "good," "$task_log" | tail -n 1)
    local good=$(echo "$last_stats" | awk '{print $1}')
    local bad=$(echo "$last_stats" | awk '{print $3}')
    local missed=$(echo "$last_stats" | awk '{print $5}')

    good=${good:-0}; bad=${bad:-0}; missed=${missed:-0}

    local num_patterns=0
    if [ -f "$tmp_dir/final.pat" ]; then
        num_patterns=$(wc -l < "$tmp_dir/final.pat")
        echo "[FINISHED] $dataset_name | $binary_name | $profile_name | ${iteration}/${ITERATIONS} | Time: ${user_time}s | RAM: ${memory_peak}KB"
        echo "$iteration,$binary_name,$profile_name,$dataset_name,$user_time,$memory_peak,$good,$bad,$missed,$num_patterns" >> "$output_file"
    else
        echo "[ERROR] $dataset_name | $binary_name | $profile_name | ${iteration}/${ITERATIONS} | Failed to generate the output file. Check $tmp_dir/time.log"
    fi

    rm -rf "$tmp_dir"
}

echo "Iteration,Binary,Profile,Dataset,UserTime(s),PeakMemory(KB),Good,Bad,Missed,Patterns" > "$OUTPUT_FILE"
echo "Results will be saved to $OUTPUT_FILE"
echo "Running up to $JOBS parallel jobs..."

for ((iteration=1; iteration<=$ITERATIONS; iteration++)); do
    for binary in "${BINARIES[@]}"; do
        if ! command -v "$binary" &> /dev/null && [ ! -f "$binary" ]; then
            echo "Binary $binary not found, skipping." >&2
            continue
        fi

        for profile in "$PROFILES_DIR"/*.in; do
            [ -e "$profile" ] || continue
            for wlh in $WLH_FILES; do
                # Check if .tr file exists before spawning background job
                tr="${wlh%.wlh}.tr"
                if [ ! -f "$tr" ]; then
                    continue
                fi

                evaluate_task "$iteration" "$binary" "$profile" "$wlh" "$OUTPUT_FILE" &

                if [[ $(jobs -r | wc -l) -ge $JOBS ]]; then
                    wait -n
                fi
            done
        done
    done
done

wait

echo "Done. Results written to $OUTPUT_FILE"
