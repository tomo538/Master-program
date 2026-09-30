#!/usr/bin/env python3
import json
import os
import math

base = os.path.abspath(os.path.dirname(__file__))
base = os.path.dirname(base)

folders = [f"dataset/BACK_{i}h" for i in range(1,13)]
start_idx = 160  # 0-based index for line 161
block_size = 60
param_names = [
    "ts",
    "optimize_days_cont",
    "pre_optlux",
    "on_time_norm",
    "duration_h"
]

all_results = []
for folder in folders:
    path = os.path.join(base, folder, "bayes_opt_log.json")
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]
    if len(lines) <= start_idx:
        print(f"{folder}: ファイルの行数が {start_idx+1} 行に満たないためスキップ")
        continue

    folder_entry = {"folder": folder, "path": path, "params": []}
    for i, param in enumerate(param_names):
        bstart = start_idx + i * block_size
        bend = bstart + block_size
        block_lines = lines[bstart:bend]
        if not block_lines:
            folder_entry["params"].append({"param": param, "error": "block empty"})
            continue
        try:
            entries = [json.loads(l) for l in block_lines]
        except Exception as e:
            folder_entry["params"].append({"param": param, "error": f"json parse error: {e}"})
            continue
        candidates = [(j, e) for j, e in enumerate(entries) if e.get('goal_complete')]
        if not candidates:
            folder_entry["params"].append({"param": param, "has_goal_complete": False})
            continue
        # choose entry with target closest to 0 (abs(target) minimal)
        best_local_idx, best_entry = min(candidates, key=lambda t: abs(t[1].get('target', math.inf)))
        best_target = best_entry.get('target')
        # position within the 60-line block (1-based)
        position_in_block = best_local_idx + 1
        global_line = bstart + best_local_idx + 1  # 1-based
        folder_entry["params"].append({
            "param": param,
            "best_target": best_target,
            "position_in_block": position_in_block,
            "local_index": best_local_idx + 1,
            "global_line": global_line,
            "params_values": best_entry.get('params')
        })
        print(f"{folder} {param}: best_target={best_target}, position_in_block={position_in_block}, global_line={global_line}")
    all_results.append(folder_entry)

out_path = os.path.join(base, 'best_per_param_summary.json')
with open(out_path, 'w', encoding='utf-8') as outf:
    json.dump(all_results, outf, ensure_ascii=False, indent=2)

print('\nSaved summary to', out_path)
