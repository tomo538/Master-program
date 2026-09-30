#!/usr/bin/env python3
import os, json, math
base = os.path.abspath(os.path.dirname(__file__))
base = os.path.dirname(base)
folders = [f"dataset/BACK_{i}h" for i in range(1,13)]
start_idx = 160
block_size = 60
param_names = ["ts","optimize_days_cont","pre_optlux","on_time_norm","duration_h"]
results = []
for folder in folders:
    path = os.path.join(base, folder, "bayes_opt_log.json")
    rec = {"folder": folder, "params": []}
    if not os.path.exists(path):
        for p in param_names:
            rec['params'].append({'param':p, 'found': False})
        results.append(rec)
        continue
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f if ln.strip()]
    if len(lines) <= start_idx:
        for p in param_names:
            rec['params'].append({'param':p, 'found': False})
        results.append(rec)
        continue
    for i,p in enumerate(param_names):
        bstart = start_idx + i*block_size
        bend = bstart + block_size
        block = lines[bstart:bend]
        if not block:
            rec['params'].append({'param':p, 'found': False})
            continue
        entries = []
        for ln in block:
            try:
                entries.append(json.loads(ln))
            except:
                entries.append(None)
        # filter only goal_complete True
        candidates = [(j,e) for j,e in enumerate(entries) if e and e.get('goal_complete')]
        if not candidates:
            rec['params'].append({'param':p, 'found': False})
            continue
        # choose candidate with target closest to 0
        best_local_idx, best_entry = min(candidates, key=lambda t: abs(t[1].get('target', math.inf)))
        position_in_block = best_local_idx + 1
        global_line = bstart + best_local_idx + 1
        rec['params'].append({
            'param': p,
            'found': True,
            'position_in_block': position_in_block,
            'global_line': global_line,
            'best_target': best_entry.get('target'),
            'params_values': best_entry.get('params')
        })
    results.append(rec)

# write markdown
md_path = os.path.join(base, 'best_per_param_goalcomplete.md')
with open(md_path, 'w', encoding='utf-8') as mf:
    mf.write('# Best per-parameter (goal_complete=True)\n\n')
    mf.write('| Parameter | ' + ' | '.join([r['folder'] for r in results]) + ' |\n')
    mf.write('|---' + '|---' * len(results) + '|\n')
    for p in param_names:
        row = [p]
        for r in results:
            info = next((x for x in r['params'] if x['param']==p), None)
            if not info or not info.get('found'):
                row.append('-')
            else:
                row.append(f"{info['position_in_block']} ({info['best_target']:.4f})")
        mf.write('| ' + ' | '.join(row) + ' |\n')

# save json summary
json_path = os.path.join(base, 'best_per_param_goalcomplete.json')
with open(json_path, 'w', encoding='utf-8') as jf:
    json.dump(results, jf, ensure_ascii=False, indent=2)

print('Saved', md_path, 'and', json_path)
