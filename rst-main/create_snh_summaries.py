# Das Skript erstellt je eine Datei je Kommentar mit der snh-Zusammenfassung in /summaries/snh.

from os import scandir
from pathlib import Path
from nltk.tree import ParentedTree
from get_core_statements import get_core_statements
from sbj_obj_extractor import Project


def make_summary_for_all_docs(directory_path):
    """
    Extracts for all documents (trees) in the directory a summary based on the
    Strong Nuclearity Hypothese. Returns a dictionary with file names as keys
    and list of lists with the core statements of the tree.

    :param directory_path: str
    :return: dict
    """
    snh_results = dict()
    with scandir(directory_path) as docs:
        for doc in docs:
            temp_inputfile = Path(directory_path + doc.name)
            temp_tree = ParentedTree.fromstring(temp_inputfile.read_text())
            temp_core_statements = get_core_statements(temp_tree)
            snh_results[doc.name.strip(".tree")] = temp_core_statements

    return snh_results


trees_subset = "trees_subset/"
results = make_summary_for_all_docs(trees_subset)

outputpath = Path("summaries/snh")
outputpath.mkdir(parents=True, exist_ok=True)

for filename, summary in results.items():
    outputfile = Path(f"{outputpath}/{filename}.txt")
    mmax_path = Path(f"pcc2.2/coreference-mmax/{filename}.mmax")
    p = Project(mmax_path)
    p.collect_tokens()
    p.collect_sentences()
    p.collect_pos()
    p.collect_refs()

    p.pos.sort()
    p.sentences.sort()
    p.pos.sort()

    with outputfile.open("w", encoding="utf-8") as ofile:
        title = summary[0]
        ofile.write(f"#{title}\n")

        # create empty rolefile
        rolefile = Path(f"{outputpath}/{filename}.roles")
        rolefile.write_text("#ROLE\tSPAN\tSENTENCE\tCOREF\tTOKENS\n")

        for s_idx, sentence in enumerate(summary[1:]):
            # write sentence to summary file
            ofile.write(f"{sentence}\n")
            
            # separate punctuation
            for sign in [",", ".", "?", "!"]:
                sentence = sentence.replace(sign, f" {sign} ")

            toks = sentence.split()

            # iterate over tokens of mmax file and find match
            for i in range(len(p.tokens) - len(toks) + 1):
                if p.tokens[i:i+len(toks)] == toks:

                    # collect entities that are in this sentence
                    possible_roles = list()
                    for role in p.pos:
                        if role.span.start >= i and role.span.stop <= i+len(toks):
                            possible_roles.append(role)

                    # save entities in a .role file (like for complete texts)
                    with rolefile.open("a", encoding="utf-8") as ofile2:
                        for rolespan in possible_roles:
                            tokens = " ".join(p.tokens[rolespan.span])

                            k = tuple((rolespan.span.start, rolespan.span.stop))
                            if k in p.coref:
                                coref = p.coref[k]
                            else:
                                coref = "_"

                            ofile2.write(
                                (f"{rolespan.role}\t"
                                f"{rolespan.span.start},{rolespan.span.stop}\t"
                                f"{s_idx}\t"
                                f"{coref}\t"
                                f"{tokens}\n")
                            )
