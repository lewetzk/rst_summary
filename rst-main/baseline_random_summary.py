# -*- coding: utf-8 -*-

# Version: Python 3.9.6
# Datum: 07.07.2022

import argparse
import os
import re
import random
from pathlib import Path
from sbj_obj_extractor import Project

from nltk import sent_tokenize


random.seed(42)


def read_text_body(txt):
    text_body = []

    # Create generator to read text
    text = (row for row in open(txt, 'r', encoding='utf-8'))
    line = next(text)
    if line == '\n' or all(tok.isupper() for tok in line.rstrip().split()):
        line = next(text)

    header = line.rstrip()
    # Make sure to skip author name/title line(s)
    while line != '\n':
        line = next(text)
    line = next(text)

    # Store commentary body
    if line != '\n':
        text_body.append(line.strip())
    for line in text:
        if line != '\n':
            text_body.append(line.strip())

    # Join text to remove mid-sentence line breaks -> tokenize sentences
    txt = " ".join(text_body)
    sents = sent_tokenize(txt, language='german')

    # Remove author id at EOF
    if re.match(r'(R.\d+)', sents[-1]) or len(sents[-1]) < 5:
        sents.pop(-1)

    return header, sents


def get_baseline_summary(txt):
    summary_dict = dict()

    header, txt_bdy = read_text_body(txt)
    first_line = txt_bdy[0]
    middle_txt_idx = len(txt_bdy)//2
    middle_line = txt_bdy[middle_txt_idx]
    last_line = txt_bdy[-1]

    summary_dict.update({"summary": [first_line, middle_line, last_line]})
    summary_dict.update({"sent_num": [0, middle_txt_idx, len(txt_bdy)]})
    summary_dict.update({"header": header})
    return summary_dict


def get_random_summary(txt):
    summary_dict = dict()
    header, txt_bdy = read_text_body(txt)
    summary = random.sample(list(enumerate(txt_bdy)), 3)
    summary_dict.update({"summary": []})
    summary_dict.update({"sent_num": []})
    summary_dict.update({"header": header})
    for idx, sent in summary:
        summary_dict["summary"].append(sent)
        summary_dict["sent_num"].append(idx)
    return summary_dict


def write_to_txt(filename, summary):
    # read mmax file
    rolefile = Path(f"{filename.parent}/{filename.stem}.roles")
    rolefile.write_text("#ROLE\tSPAN\tSENTENCE\tCOREF\tTOKENS\n")

    mmax_path = Path(f"pcc2.2/coreference-mmax/{filename.stem}.mmax")
    p = Project(mmax_path)
    p.collect_tokens()
    p.collect_sentences()
    p.collect_pos()
    p.collect_refs()

    p.pos.sort()
    p.sentences.sort()
    p.pos.sort()

    

    with filename.open("w", encoding="utf-8") as ofile:
        ofile.write(f"#{summary['header']}\n")
        
        for new_sent_idx, (sentence, sent_index) in enumerate(zip(summary["summary"], summary["sent_num"])):
            ofile.write(f"{sent_index}\t{sentence}\n")

            for sign in [",", ".", "?", "!", ":", ";"]:
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
                                f"{new_sent_idx}\t"
                                f"{coref}\t"
                                f"{tokens}\n")
                            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus_path', type=str, help="path to corpus")
    args = parser.parse_args() # these paths are in the primary data folder in pcc2.2

    #dir_path = Path("gold-pcc/bracketed_files")


    #  Creates paths for summary folders
    baseline_path = Path("summaries/baseline")
    random_path = Path("summaries/random")

    # create directories if they don't exists
    baseline_path.mkdir(parents=True, exist_ok=True)
    random_path.mkdir(parents=True, exist_ok=True)


    # Create summary dict for all summaries with sentences and sentence numbers
    # print summaries to txt and print dict to json
    for filename in os.listdir(Path(args.corpus_path)):
        complete_path = Path(f"{args.corpus_path}/{filename}")

        # baseline summary
        baseline_summary = get_baseline_summary(complete_path)
        b_output_file = Path(f"{baseline_path}/{filename}")
        write_to_txt(b_output_file, baseline_summary)

        # random summary
        random_summary = get_random_summary(complete_path)
        r_output_file = Path(f"{random_path}/{filename}")
        write_to_txt(r_output_file, random_summary)


if __name__ == '__main__':
    #  python baseline_random_summary.py pcc2.2/primary-data/
    main()
