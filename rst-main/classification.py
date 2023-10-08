import itertools
from pathlib import Path

import numpy as np
from separate_train_test_sets import split_dataset
from create_vector import create_vector
from create_entity_grid import create_entity_grid

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

import torch
from transformers import AutoTokenizer, AutoModel


np.random.seed(42)
tokenizer = AutoTokenizer.from_pretrained(
    "T-Systems-onsite/german-roberta-sentence-transformer-v2"
    )
roberta = AutoModel.from_pretrained(
    "T-Systems-onsite/german-roberta-sentence-transformer-v2"
)


def read_vectors(path):
    vectors = dict()
    with open(path, encoding="utf-8") as infile:
        for line in infile:
            if not line.startswith("#"):
                key, *vector = line.strip().split("\t")
                vectors[key] = np.array(vector, dtype=float)
    return vectors


def get_summs(text, path):
    # open summary
    role_file = Path(f"{path}/{text}.roles").read_text()
    role_file = role_file.strip().split("\n")
    roles = [line.split("\t") for line in role_file if not line.startswith("#")]
    
    summary = Path(f"{path}/{text}.txt").read_text().split("\n")
    summary = [i for i in summary if not i.startswith("#") and i != ""]  # remove title and empty lines
    grid = create_entity_grid(roles, len(summary))
    
    # save grid
    grid_file = Path(f"{path}/{text}.grid")
    with grid_file.open("w", encoding="utf-8") as ofile:
        for line in grid:
            ofile.write("\t".join(line))
            ofile.write("\n")

    return create_vector(grid)


def summary_as_text(folder, text):
    string = ""
    for line in Path(f"summaries/{folder}/{text}.txt").read_text().split("\n"):
        if not line.startswith("#"):
            string += line.split("\t")[-1]
            string += " "
    return string.strip()


def get_bert_vector(texts):
    data = list()
    labels = list()
    for text in texts:
        try:            
            baseline = summary_as_text("baseline", text)
            random = summary_as_text("random", text)
            gold = summary_as_text("gold", text)

            with torch.no_grad():
                random = roberta(**tokenizer(random, return_tensors="pt"))[1]
                gold = roberta(**tokenizer(gold, return_tensors="pt"))[1]
                baseline = roberta(**tokenizer(baseline, return_tensors="pt"))[1]

            summ = [gold, baseline, random]
            for tup in itertools.combinations(summ, 2):
                data.append(tup[0].numpy() - tup[1].numpy())
                labels.append(1)

                # balance data:
                data.append(tup[1].numpy() - tup[0].numpy())
                labels.append(0)

        except FileNotFoundError:
            print(f"missing file: {text}")

    return np.array(data).squeeze(), np.array(labels)


def get_entity_vectors(texts):
    data = list()
    labels = list()
    # for each text create a list
    for text in texts:
        try:
            baseline = get_summs(text, Path("summaries/baseline"))
            random = get_summs(text, Path("summaries/random"))
            gold = get_summs(text, Path("summaries/gold"))

            summ = [gold, baseline, random]
            for tup in itertools.combinations(summ, 2):
                if tup[0] != tup[1]:  # vectors must be different!
                    data.append(np.array(tup[0]) - np.array(tup[1]))
                    labels.append(1)

                    # balance data:
                    data.append((np.array(tup[-1]) - np.array(tup[0])))
                    labels.append(0)

        except FileNotFoundError:
            print(f"missing file: {text}")

    return np.array(data), np.array(labels)


def main():
    vecs = read_vectors("vectors.txt")
    print("#---ENTITY GRID EMBEDDING---#")

    # collect and split data
    data, labels = get_entity_vectors(vecs.keys())
    x_train, x_test, y_train, y_test = train_test_split(data, labels)    

    # train and evaluate SVM
    svm = SVC(gamma='auto', kernel="linear")
    svm.fit(x_train, y_train)
    correct = (svm.predict(x_test) == y_test).sum()
    print(f"Result SVM entity grid: {correct} out of {len(y_test)}")

    ## BERT
    print("\n\n#---BERT EMBEDDING---#")
    # collect and split data
    data, labels = get_bert_vector(vecs.keys())
    x_train, x_test, y_train, y_test = train_test_split(data, labels)
  
    # train and evaluate SVM
    svm = SVC(gamma='auto', kernel="linear")
    svm.fit(x_train, y_train)
    correct = (svm.predict(x_test) == y_test).sum()
    print(f"Result BERT embedding: {correct} out of {len(y_test)}")

    # classify snh, neural
    print("\n\n#---CLASSIFY SUMMARIES---#")
    outputfile = Path("classification_result.txt")
    with outputfile.open("w", encoding="utf-8") as ofile:
        for text in sorted(vecs.keys()):
            try:
                gold = summary_as_text("gold", text)
                baseline = summary_as_text("baseline", text)
                random = summary_as_text("random", text)
                neural25 = summary_as_text("neural/25k", text)
                neural50 = summary_as_text("neural/50k", text)
                snh = summary_as_text("snh", text)

                with torch.no_grad():
                    random = roberta(**tokenizer(random, return_tensors="pt"))[1]
                    gold = roberta(**tokenizer(gold, return_tensors="pt"))[1]
                    baseline = roberta(**tokenizer(baseline, return_tensors="pt"))[1]
                    neural25 = roberta(**tokenizer(neural25, return_tensors="pt"))[1]
                    neural50 = roberta(**tokenizer(neural50, return_tensors="pt"))[1]
                    snh = roberta(**tokenizer(snh, return_tensors="pt"))[1]

                order = np.array(["random", "gold", "baseline", "neural25", "neural50", "snh"])
                result = np.dot(np.concatenate([random, gold, baseline, neural25, neural50, snh]), svm.coef_.T)
                sorted_order = np.argsort(result, axis=0)
                to_print = "\t".join(order[sorted_order].squeeze())
                ofile.write(f"{text}\t{to_print}\n")

            except FileNotFoundError:
                print(f"missing file: {text}")


if __name__ == "__main__":
    main()
