#! /usr/bin/env python3

from owlready2 import *

import sys

# sys.setrecursionlimit(10000)

onto_path.append('/home/damien/Workspace/master_project/data/ontologies')
onto = get_ontology('onto1_correct.owl')
# onto = get_ontology('kr-owlxml.owl')
onto.load()

for item in onto.classes():
    print(item)
