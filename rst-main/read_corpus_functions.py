def read_summary(path):
    corpus = dict()
    for item in os.listdir(path):
        with Path(f"{path}/{item}").open(encoding="utf-8") as infile:
            sents = list()
            sent_num = list()
            for line in infile:
                if line.startswith("#"):
                    header = line.strip().replace("#", "")
                else:
                    try:
                        # all but snh
                        idx, sent = line.strip().split("\t")
                        sent_num.append(idx)
                    except ValueError:
                        # snh have no sentence index
                        sent = line.strip()
                    sents.append(sent)
            corpus[item]["summary"] = sents
            corpus[item]["sent_num"] = sent_num
            corpus[item]["header"] = header
    return corpus


def read_grids(path):
    corpus = dict()
    for element in Path(path).iterdir():
        with element.open(encoding="utf-8") as infile:
            this_grid = list()
            for line in infile:
                line = line.strip().split("\t")
                this_grid.append(line)

        corpus[element.stem] = this_grid

    return corpus


def read_vectors(path):
    vectors = list()
    with open(path, encoding="utf-8") as infile:
        for line in infile:
            if not line.startswith("#"):
                key, *vector = line.strip().split("\t")
                vectors.append(vector)
    return np.array(vectors, dtype=float)