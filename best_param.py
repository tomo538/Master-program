import json

input_file = "dataset/BACK_8h/bayes_opt_log.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

param_names = [
    "ts",
    "optimize_days_cont",
    "pre_optlux",
    "on_time_norm",
    "duration_h"
]

start = 160      # 161行目（0始まり）
block_size = 60

best_results = []

for i, param in enumerate(param_names):
    block = data[start + i * block_size : start + (i + 1) * block_size]

    # goal_complete=True のものだけ抽出
    candidates = [row for row in block if row["goal_complete"]]

    if not candidates:
        print(f"{param}: goal_complete=True のデータがありません")
        continue

    # target が最小のものを取得
    best = min(candidates, key=lambda x: x["target"])
    best_results.append(best)

    print(f"=== {param} ===")
    print(f"target = {best['target']}")
    print(f"{param} = {best['params'][param]}")
    print()

"""# 保存
with open("best_results.jsonl", "w", encoding="utf-8") as f:
    for row in best_results:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")"""