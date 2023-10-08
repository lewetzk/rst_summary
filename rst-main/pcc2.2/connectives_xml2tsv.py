import os
import re
import sys
import csv
import codecs
from lxml import etree

xmlParser = etree.XMLParser(strip_cdata=False, resolve_entities=False, encoding = 'utf-8', remove_comments=True, remove_blank_text=True)

def get_relations(cfolder):

    relations = []
    for cf in os.listdir(cfolder):
        acf = os.path.join(cfolder, cf)
        tree = etree.parse(os.path.join(cfolder, acf), parser=xmlParser)
        for rel in tree.getroot().findall('.//relation'):
            fd = {}
            for ct in rel.findall('.//connective_token'):
                fd[int(ct.get('id'))] = ct.get('token')
            for iat in rel.findall('.//int_arg_token'):
                fd[int(iat.get('id'))] = iat.get('token')
            for eat in rel.findall('.//ext_arg_token'):
                fd[int(eat.get('id'))] = eat.get('token')
            fulltext = ' '.join([x[1] for x in sorted(fd.items(), key = lambda x: x[0])])
            r = {'File': cf,
                 'Relation ID': rel.get('relation_id'),
                 'PDTB3 sense': rel.get('pdtb3_sense'),
                 'Type': rel.get('type'),
                 'Connective': ' '.join([x.get('token') for x in rel.findall('.//connective_token')]),
                 'External argument': ' '.join([x.get('token') for x in rel.findall('.//ext_arg_token')]),
                 'Internal argument': ' '.join([x.get('token') for x in rel.findall('.//int_arg_token')]),
                 'Full text': fulltext
            }
            relations.append(r)

    return relations

def to_tsv(relations, outfile):

    columns = ['File', 'Relation ID', 'PDTB3 sense', 'Type', 'Connective', 'External argument', 'Internal argument', 'Full text']
    writer = csv.DictWriter(codecs.open(outfile, 'w'), delimiter='\t', quoting=csv.QUOTE_MINIMAL, fieldnames=columns)
    writer.writeheader()
    for r in relations:
        writer.writerow(r)
    

if __name__ == '__main__':

    connectives_folder = os.path.join(os.getcwd(), 'connectives')
    relations = get_relations(connectives_folder)

    tsv_out = 'pcc_discourse_relations_all.tsv'
    to_tsv(relations, tsv_out)
