import argparse
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path
import re
import xml.etree.ElementTree as ET


@total_ordering
@dataclass
class RoleSpan:
    span: slice
    role: str

    def __lt__(self, other):
        return self.span < other.span


class Project:
    def __init__(self, pathfile):
        self.path = pathfile.parent
        self.file = pathfile.stem
        self.tokens = list()
        self.pos = list()
        self.sentences = list()
        self.temp = dict()
        self.coref = dict()

    def parse_span(self, span):
        r = re.findall("[0-9]+", span)
        if len(r) == 1:
            sen = slice(int(r[0])-1, int(r[0]))
        else:
            sen = slice(int(r[0])-1, int(r[1]))
        return sen

    def get_coref_set(self, coref, tok_counter):
        """
        extract golden coreference clusters
        """
        # check if coreference sets are being opened or closed
        opening_sets = re.findall(r"\((\d+)", coref)
        closing_sets = re.findall(r"(\d+)\)", coref)

        # start a new coreference cluster for each opening set
        for oset in opening_sets:
            if oset not in self.temp:
                self.temp[oset] = []

            # use a "stack" to keep track of nested mentions
            self.temp[oset].append([])

        # add current token to all opened coreference clusters
        for key in self.temp:
            if len(self.temp[key]) > 0:
                for i in range(len(self.temp[key])):
                    self.temp[key][i].append(tok_counter)

        # save and close all closing coreference clusters
        for cset in closing_sets:
            if cset not in self.coref:
                self.coref[cset] = []
            self.coref[cset].append(self.temp[cset][-1])
            del self.temp[cset][-1]

    def collect_tokens(self):
        """
        retrieve tokens from the MMAX project
        """
        words = Path(f"{self.path}/basedata/{self.file}_words.xml")
        tree = ET.parse(words)
        for child in tree.getroot():
            self.tokens.append(child.text)

    def collect_pos(self):
        """
        retrieve POS tags from the MMAX project
        """
        pos = Path(f"{self.path}/markables/{self.file}_primmark_level.xml")
        tree = ET.parse(pos)
        for child in tree.getroot():
            span = self.parse_span(child.attrib["span"])
            role = child.attrib["grammatical_role"]
            self.pos.append(RoleSpan(span, role))

    def collect_sentences(self):
        """
        retrieve sentences from the MMAX project
        """
        sentence = Path(f"{self.path}/markables/{self.file}_sentence_level.xml")
        tree = ET.parse(sentence)
        for child in tree.getroot():
            span = self.parse_span(child.attrib["span"])
            self.sentences.append(span)

    def collect_refs(self):
        """
        retrieve references from the MMAX project
        saved as tuples of indices
        """
        coref = Path(f"{self.path.parent}/coreference-conll/{self.file}.conll")
        with coref.open(encoding="utf-8") as infile:
            tok_counter = 0
            for line in infile:
                line = line.strip()

                if line == "" or line.startswith("#"):
                    pass

                else:
                    line = line.split("\t")
                    if line[-1] != "_":
                        self.get_coref_set(line[-1], tok_counter)

                    tok_counter += 1

        # invert coref dict for easier access
        temp = dict()
        for key, value in self.coref.items():
            for item in value:
                temp[tuple((item[0], item[-1] + 1))] = key
        self.coref = temp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        help="input directory containing MMAX files"
    )
    parser.add_argument(
        "output",
        help="output directory"
    )
    args = parser.parse_args()

    dir_name = Path(args.directory)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_name in dir_name.iterdir():
        if str(file_name).endswith(".mmax"):
            p = Project(file_name)
            p.collect_tokens()
            p.collect_sentences()
            p.collect_pos()
            p.collect_refs()

            p.pos.sort()
            p.sentences.sort()

            output_file = Path(f"{output_dir}/{p.file}.roles")
            with output_file.open("w", encoding="utf-8") as ofile:
                sentence_idx = 0

                # write file header (only line that starts with #)
                ofile.write(
                    "#ROLE\tSPAN\tSENTENCE\tCOREF\tTOKENS\n"
                )

                for rolespan in p.pos:
                    while (sentence_idx != len(p.sentences) - 1 and
                            (rolespan.span.start
                             > p.sentences[sentence_idx].start)):
                        sentence_idx += 1

                    k = tuple((rolespan.span.start, rolespan.span.stop))
                    if k in p.coref:
                        coref = p.coref[k]
                    else:
                        coref = "_"

                    tokens = " ".join(p.tokens[rolespan.span])

                    ofile.write(
                        (f"{rolespan.role}\t"
                         f"{rolespan.span.start},{rolespan.span.stop}\t"
                         f"{sentence_idx}\t"
                         f"{coref}\t"
                         f"{tokens}\n")
                    )


if __name__ == "__main__":
    main()
