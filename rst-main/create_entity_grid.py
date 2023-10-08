import csv
from os import scandir, makedirs
from pathlib import Path

from sbj_obj_extractor import Project


def get_roles_from_doc(in_file):
    """Returns a list of lists with the lines from the role file
    # ['#ROLE', 'SPAN', 'SENTENCE', 'COREF', 'TOKENS']"""
    doc_roles = []
    with open(in_file, 'r', newline='') as csv_f:
        csv_reader = csv.reader(csv_f, delimiter='\t', quotechar='|')
        for row in csv_reader:
            doc_roles.append(row)

    return doc_roles


def create_entity_grid(doc_roles, num_of_sents):
    """
    input: doc_roles: list of splitted lines from a .role file
    """
    # maps the coreference numbers to the index from the entity matrix
    coref_to_idx = {}
    idx = 0
    for line in doc_roles[1:]:
        temp_coref = line[-2]

        if temp_coref not in coref_to_idx:
            coref_to_idx[temp_coref] = idx
            idx += 1

    num_of_entities = len(coref_to_idx)

    # create matrix with num of sentence rows and num of entities columns
    entity_matrix = [["-" for i in range(num_of_entities)] for j in range(num_of_sents)]
    for line in doc_roles[1:]:
        coref = line[-2]
        sent_num = int(line[2]) - 1
        coref_idx = coref_to_idx[coref]

        if line[0] == "indir-obj":
            entity_matrix[sent_num][coref_idx] = "x"
        elif line[0] == "dir-obj":
            entity_matrix[sent_num][coref_idx] = "o"
        elif line[0] == "sbj":
            entity_matrix[sent_num][coref_idx] = "s"

    return entity_matrix


def extract_entity_grid_for_all_docs(directory_path):
    """
    Extracts for all documents in the directory a entity grid (list of lists).
    Returns a dictionary with file names as keys
    and list of lists with the entity grid.

    :param directory_path: str
    :return: dict
    """
    entity_grids = dict()
    with scandir(directory_path) as docs:
        for doc in docs:
            
            doc_roles = get_roles_from_doc(doc)
            # get number of sentences from MMAX file (always remove 1, the title is annotated as sentence)
            # there is probably a better way to do this but...
            filename = Path(doc).stem     
            p = Project(Path(f"pcc2.2/coreference-mmax/{filename}.mmax"))
            p.collect_tokens()
            p.collect_sentences()

            p.pos.sort()
            p.sentences.sort()
            p.pos.sort()

            num_of_sents = len(p.sentences) - 1  # remove title sentence
            entity_matrix = create_entity_grid(doc_roles, num_of_sents)
            entity_grids[doc.name.strip(".roles").lstrip("roles/")] = entity_matrix

    return entity_grids


def main():
    result = extract_entity_grid_for_all_docs("roles/")

    # save to text files
    makedirs("grids", exist_ok=True)
    for key, value in result.items():
        with open(Path(f"grids/{key}.grid"), "w", encoding="utf-8") as ofile:
            for line in value:
                to_write = "\t".join(line)
                ofile.write(f"{to_write}\n")


if __name__ == "__main__":
    main()