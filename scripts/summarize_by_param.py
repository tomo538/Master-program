#!/usr/bin/env python3
import json
import os

base = os.path.abspath(os.path.dirname(__file__))
base = os.path.dirname(base)
summary_path = os.path.join(base, 'best_per_param_summary.json')
if not os.path.exists(summary_path):
    raise SystemExit('best_per_param_summary.json not found')

with open(summary_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

param_names = ["ts","optimize_days_cont","pre_optlux","on_time_norm","duration_h"]

# build mapping param -> list of (folder, position_in_block or '-')
result = {p: [] for p in param_names}
for entry in data:
    folder = entry.get('folder')
    params = entry.get('params', [])
    # create dict param->info
    pd = {p['param']: p for p in params}
    for p in param_names:
        info = pd.get(p)
        if not info or not info.get('position_in_block'):
            result[p].append((folder, '-'))
        else:
            result[p].append((folder, info.get('position_in_block')))

# print table
print('Parameter-wise positions (position in 60-entry block)')
headers = ['param'] + [e.get('folder') for e in data]
print('\t'.join(headers))
for p in param_names:
    row = [p] + [str(v[1]) for v in result[p]]
    print('\t'.join(row))

# save CSV
csv_path = os.path.join(base, 'best_per_param_positions.csv')
with open(csv_path, 'w', encoding='utf-8') as cf:
    cf.write(','.join(headers) + '\n')
    for p in param_names:
        cf.write(','.join([p] + [str(v[1]) for v in result[p]]) + '\n')

print('\nCSV saved to', csv_path)
