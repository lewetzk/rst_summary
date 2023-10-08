import json
from pathlib import Path


def count_category_rankings(rank_results_list):
    count_dict = dict()
    for cat in ["random", "gold", "baseline", "neural25", "neural50", "snh"]:
        for rank in ["first", "second", "third", "fourth", "fifth", "sixth"]:
            subdict = f"{cat}_{rank}"
            if subdict not in count_dict:
                count_dict.update({subdict: 0})

    item_counter = 0
    for txt in rank_results_list:
        if txt[5] == "random":
            count_dict["random_first"] += 1
        if txt[5] == "snh":
            count_dict["snh_first"] += 1
        if txt[5] == "gold":
            count_dict["gold_first"] += 1
        if txt[5] == "baseline":
            count_dict["baseline_first"] += 1
        if txt[5] == "neural25":
            count_dict["neural25_first"] += 1
        if txt[5] == "neural50":
            count_dict["neural50_first"] += 1

        if txt[4] == "random":
            count_dict["random_second"] += 1
        if txt[4] == "snh":
            count_dict["snh_second"] += 1
        if txt[4] == "gold":
            count_dict["gold_second"] += 1
        if txt[4] == "baseline":
            count_dict["baseline_second"] += 1
        if txt[4] == "neural25":
            count_dict["neural25_second"] += 1
        if txt[4] == "neural50":
            count_dict["neural50_second"] += 1

        if txt[3] == "random":
            count_dict["random_third"] += 1
        if txt[3] == "snh":
            count_dict["snh_third"] += 1
        if txt[3] == "gold":
            count_dict["gold_third"] += 1
        if txt[3] == "baseline":
            count_dict["baseline_third"] += 1
        if txt[3] == "neural25":
            count_dict["neural25_third"] += 1
        if txt[3] == "neural50":
            count_dict["neural50_third"] += 1

        if txt[2] == "random":
            count_dict["random_fourth"] += 1
        if txt[2] == "snh":
            count_dict["snh_fourth"] += 1
        if txt[2] == "gold":
            count_dict["gold_fourth"] += 1
        if txt[2] == "baseline":
            count_dict["baseline_fourth"] += 1
        if txt[2] == "neural25":
            count_dict["neural25_fourth"] += 1
        if txt[2] == "neural50":
            count_dict["neural50_fourth"] += 1

        if txt[1] == "random":
            count_dict["random_fifth"] += 1
        if txt[1] == "snh":
            count_dict["snh_fifth"] += 1
        if txt[1] == "gold":
            count_dict["gold_fifth"] += 1
        if txt[1] == "baseline":
            count_dict["baseline_fifth"] += 1
        if txt[1] == "neural25":
            count_dict["neural25_fifth"] += 1
        if txt[1] == "neural50":
            count_dict["neural50_fifth"] += 1

        if txt[0] == "random":
            count_dict["random_sixth"] += 1
        if txt[0] == "snh":
            count_dict["snh_sixth"] += 1
        if txt[0] == "gold":
            count_dict["gold_sixth"] += 1
        if txt[0] == "baseline":
            count_dict["baseline_sixth"] += 1
        if txt[0] == "neural25":
            count_dict["neural25_sixth"] += 1
        if txt[0] == "neural50":
            count_dict["neural50_sixth"] += 1

        item_counter += 1
    print(f"Gesamtzahl Kommentare: {item_counter}\n")
    return count_dict

# Count firsts/secs/thirds for each result category
rankfile = Path("classification_result.txt")
with rankfile.open("r", encoding="utf-8") as f:
    ft = f.readlines()
    all_lines = []
    for line in ft:
        txt_rks = line.rstrip().split(sep="\t")[1:]
        all_lines.append(txt_rks)

# How often is snh > gold, snh > baseline?
snh_gt_gold_counter = 0
gold_gt_snh_counter = 0

snh_gt_baseline_counter = 0
baseline_gt_snh_counter = 0

snh_gt_neural25_counter = 0
neural25_gt_snh_counter = 0

snh_gt_neural50_counter = 0
neural50_gt_snh_counter = 0

snh_gt_random_counter = 0
random_gt_snh_counter = 0

for txt in all_lines:
    if txt.index("snh") > txt.index("gold"):
        snh_gt_gold_counter += 1
    if txt.index("gold") > txt.index("snh"):
        gold_gt_snh_counter += 1

    if txt.index("snh") > txt.index("baseline"):
        snh_gt_baseline_counter += 1
    if txt.index("baseline") > txt.index("snh"):
        baseline_gt_snh_counter += 1

    if txt.index("snh") > txt.index("neural25"):
        snh_gt_neural25_counter += 1
    if txt.index("neural25") > txt.index("snh"):
        neural25_gt_snh_counter += 1

    if txt.index("snh") > txt.index("neural50"):
        snh_gt_neural50_counter += 1
    if txt.index("neural50") > txt.index("snh"):
        neural50_gt_snh_counter += 1

    if txt.index("snh") > txt.index("random"):
        snh_gt_random_counter += 1
    if txt.index("random") > txt.index("snh"):
        random_gt_snh_counter += 1

print(f"snh besser als gold: {snh_gt_gold_counter}              gold besser als snh: {gold_gt_snh_counter}")
print(f"snh besser als baseline: {snh_gt_baseline_counter}          baseline besser als snh: {baseline_gt_snh_counter}")
print(f"snh besser als neural25: {snh_gt_neural25_counter}          neural25 besser als snh: {neural25_gt_snh_counter}")
print(f"snh besser als neural50: {snh_gt_neural50_counter}          neural50 besser als snh: {neural50_gt_snh_counter}")
print(f"snh besser als random: {snh_gt_random_counter}           random besser als snh: {random_gt_snh_counter}\n")

human_rank = count_category_rankings(all_lines)

# Kurzübersicht firsts/seconds
for key, val in human_rank.items():
    if "first" in key:
        print(f"No of {key}: {val}")
    if "second" in key:
        print(f"No of {key}: {val}\n")

# Zusammenfassungsart mit den meisten firsts
max_val = [key for key, value in human_rank.items() if value == max(human_rank.values())]
print(f"Beste Zusammenfassungen: {max_val[0]}")

with open('human_readable_rank_results.json', 'w', encoding='utf8') as json_file:
    json.dump(human_rank, json_file, ensure_ascii=False, indent=6)
