#!/usr/bin/env python3
import json
import os

base = os.path.abspath(os.path.dirname(__file__))
base = os.path.dirname(base)

folders = [f"dataset/BACK_{i}h" for i in range(1,13)]
start_idx = 160  # 0-based index for line 161
block_size = 60

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
    lines = lines[start_idx:]

    num_blocks = (len(lines) + block_size - 1) // block_size
    folder_results = []
    for b in range(num_blocks):
        block_lines = lines[b*block_size:(b+1)*block_size]
        if not block_lines:
            continue
        try:
            entries = [json.loads(l) for l in block_lines]
        except Exception as e:
            print(f"{folder} block {b}: JSON parse error: {e}")
            continue
        # find candidates with goal_complete True
        candidates = [(i, e) for i, e in enumerate(entries) if e.get('goal_complete')]
        if not candidates:
            # record no candidate
            folder_results.append({
                'block': b,
                'has_goal_complete': False,
            })
            continue
        # find min target among candidates
        min_target = min(e[1].get('target', float('inf')) for e in candidates)
        # find first occurrence index within the block among entries
        first_local_idx = next((i for i, e in enumerate(entries) if e.get('goal_complete') and e.get('target') == min_target), None)
        if first_local_idx is None:
            folder_results.append({
                'block': b,
                'has_goal_complete': True,
                'error': 'min target not found in block'
            })
            continue
        global_line = start_idx + b*block_size + first_local_idx + 1  # 1-based line number
        best_entry = entries[first_local_idx]
        folder_results.append({
            'block': b,
            'has_goal_complete': True,
            'best_target': min_target,
            'local_index': first_local_idx + 1,  # 1-based within block
            'global_line': global_line,
            'params': best_entry.get('params'),
        })
        print(f"{folder} block {b}: best_target={min_target}, global_line={global_line}")
    all_results.append({'folder': folder, 'results': folder_results})

out_path = os.path.join(base, 'best_blocks_summary.json')
with open(out_path, 'w', encoding='utf-8') as outf:
    json.dump(all_results, outf, ensure_ascii=False, indent=2)

print('\nSaved summary to', out_path)
