#! /usr/bin/env python3

from owlready2 import *
import os
import yaml


def load_config(file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config


def load_ontologies(ontology_path):  # ontology_name
    # Take the ontologies path and load all ontologies in directory
    list_ontologies = os.listdir(ontology_path)
    onto_path.append(ontology_path)

    i = 0

    for ontology in list_ontologies:
        if i < 1:
            onto = get_ontology(ontology).load()
            i = i + 1
            # onto.load()
        else:
            onto_add = get_ontology(ontology).load()
            #print(onto_add)
            print(onto.imported_ontologies.append(onto_add))
            # onto = get_ontology(ontology)
            print(onto)

    onto.load()
    print(onto)

    b = 0

    for item in onto.classes():
        print(item)
        b = b + 1

    print(b)



def collect_concept_name():
    pass


def onto_main(config_file):
    """Main function"""

    config = load_config(config_file)
    onto_path = config['ontologies']['path']
    load_ontologies(onto_path)


if __name__ == '__main__':

    # load file configuration
    config_file = 'config/config_ontologies.yml'
    onto_main(config_file)


    """
    onto_path.append('/home/damien/Workspace/master_project/data/ontologies')
    # onto = get_ontology('kr-owlxml.owl')
    onto = get_ontology('onto1_correct.owl')
    onto.load()

    for item in onto.classes():
        print(item)

    """
