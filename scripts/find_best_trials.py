#!/usr/bin/env python3
import json
import os

base = os.path.abspath(os.path.dirname(__file__))
base = os.path.dirname(base)  # workspace root

folders = [f"dataset/BACK_{i}h" for i in range(1,13)]

results = []
for folder in folders:
    path = os.path.join(base, folder, "bayes_opt_log.json")
    if not os.path.exists(path):
        print(f"MISSING: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # use only lines from 161行目以降 (1-based) → index 160以降 (0-based)
    start_idx = 160
    if len(lines) <= start_idx:
        print(f"{folder}: ファイルの行数が {start_idx+1} 行に満たないため処理をスキップします")
        continue
    lines = lines[start_idx:]
    if not lines:
        print(f"EMPTY: {path}")
        continue
    entries = [json.loads(line) for line in lines]

    # candidates where goal_complete is true
    candidates = [(i + 1, e) for i, e in enumerate(entries) if e.get("goal_complete")]
    if not candidates:
        print(f"{folder}: goal_complete=True のデータがありません")
        continue

    best_target = min(e[1].get("target", float('inf')) for e in candidates)
    # first occurrence index among all entries
    first_idx = next((i + 1 for i, e in enumerate(entries) if e.get("goal_complete") and e.get("target") == best_target), None)
    # collect best entry(s)
    best_entries = [e for i, e in candidates if e.get("target") == best_target]

    out = {
        "folder": folder,
        "path": path,
        "best_target": best_target,
        "first_line": first_idx,
        "num_candidates": len(candidates),
        "example_params": best_entries[0].get("params") if best_entries else None,
    }
    results.append(out)
    print(f"{folder}: best_target={best_target}, first_line={first_idx}, num_goal_complete={len(candidates)}")
    print(f"  example params: {out['example_params']}")

# Save summary
summary_path = os.path.join(base, "best_trials_summary.json")
with open(summary_path, "w", encoding="utf-8") as sf:
    json.dump(results, sf, ensure_ascii=False, indent=2)

print('\nSummary saved to', summary_path)
