from pathlib import Path
import os


def read_corpus(path):
    corpus = dict()
    for item in os.listdir(path):
        with Path(f"{path}/{item}").open(encoding="utf-8") as infile:
            sents = list()
            for line in infile:
                try:
                    # all but snh
                    idx, sent = line.strip().split("\t")
                except ValueError:
                    sent = line.strip()
                sents.append(sent)
            corpus[item] = sents
    return corpus


def evaluate(snh_results, gold_results):
    true_positive = 0
    accuracy = 0
    false_negative = 0

    for summary_key in snh_results.keys():
        if summary_key in gold_results:
            gold_sum = gold_results[summary_key]
            snh_sum = snh_results[summary_key]

            for edu in snh_sum:
                if edu in gold_sum:
                    true_positive += 1
                else:
                    false_negative += 1

    return true_positive, false_negative

if __name__ == "__main__":
    snh = read_corpus(Path("summaries/snh"))
    gold = read_corpus(Path("summaries/gold"))
    tp, fn = evaluate(snh, gold)

    print(f"True Positives: {tp}")
    print(f"False Negatives: {fn}")