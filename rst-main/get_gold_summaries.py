from os import scandir
from pathlib import Path
import regex as re
from sbj_obj_extractor import Project


def get_gold_summaries(directory_path):
    gold_results = dict()
    pattern = re.compile(r"\[([^\]]+)]([0-9])")
    with scandir(directory_path) as docs:
        for doc in docs:
            with open(doc, 'r', encoding="utf-8") as f:
                temp_summary = []
                for i, line in enumerate(f):
                    result = pattern.search(line) 
                    if result is not None:
                        sentence = result.group(1)
                        temp_summary.append((i, sentence))
                gold_results[doc.name] = temp_summary

    return gold_results


gold_path = "gold-pcc/bracketed_files"
results = get_gold_summaries(gold_path)

outputpath = Path("summaries/gold")
outputpath.mkdir(parents=True, exist_ok=True)

for filename, summary in results.items():
    outputfile = Path(f"{outputpath}/{filename}")
    rolefile = Path(f"{outputpath}/{filename.replace('.txt', '')}.roles")
    rolefile.write_text("#ROLE\tSPAN\tSENTENCE\tCOREF\tTOKENS\n")
    mmax_path = Path(f"pcc2.2/coreference-mmax/{filename.replace('.txt', '')}.mmax")
    p = Project(mmax_path)
    p.collect_tokens()
    p.collect_sentences()
    p.collect_pos()
    p.collect_refs()

    p.pos.sort()
    p.sentences.sort()
    p.pos.sort()

    with outputfile.open("w", encoding="utf-8") as ofile:
        for new_index, (idx, sentence) in enumerate(summary):
            ofile.write(f"{idx}\t{sentence}\n")

            for sign in [",", ".", "?", "!"]:
                sentence = sentence.replace(sign, f" {sign} ")

            toks = sentence.split()

            # iterate over tokens of mmax fiile and find match
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
                                f"{new_index}\t"
                                f"{coref}\t"
                                f"{tokens}\n")
                            )
