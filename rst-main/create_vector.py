import json
import itertools
from collections import defaultdict
from pathlib import Path


# create a transition to index dict to keep track of order of elements
entities = ["s", "o", "x", "-"]
transition_to_index = dict()
for i, value in enumerate(itertools.product(entities, entities)):
    transition = "".join(value)
    transition_to_index[transition] = i


def read_corpus(path):
    corpus = dict()
    for element in Path(path).iterdir():
        with element.open(encoding="utf-8") as infile:
            this_grid = list()
            for line in infile:
                line = line.strip().split("\t")
                this_grid.append(line)

        corpus[element.stem] = this_grid

    return corpus


def create_vector(grid):
    # create empty vector and count dict
    vector = [0 for i in range(len(transition_to_index))]
    if len(grid) == 0:
        return vector
    tot_transitions = len(grid[0]) * (len(grid) - 1)
    transitions = defaultdict(int)

    # iterate over grid and extract counts
    for i in range(len(grid) - 1):
        line = grid[i]
        for j, element in enumerate(line):
            this_transition = "".join((element, grid[i+1][j]))
            transitions[this_transition] += 1

    # calculate probabilty of each transition and populate vector
    for key, value in transitions.items():
        position = transition_to_index[key]
        vector[position] = value / tot_transitions

    return vector


def main():
    data = read_corpus("grids")

    result = dict()
    for key, value in data.items():
        result[key] = create_vector(value)


    with open("vectors.txt", "w", encoding="utf-8") as ofile:
        header = "\t".join(transition_to_index.keys())
        ofile.write(f"#filename\t{header}\n")
        for key, value in sorted(result.items()):
            line = f"{key}\t" + "\t".join([str(round(i, 6)) for i in value])
            ofile.write(f"{line}\n")


if __name__ == "__main__":
    main()