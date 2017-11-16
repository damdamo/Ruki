#! /usr/bin/env python3

from owlready2 import *
import os
import yaml


def load_config(file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config


def return_concept_name(ontology):
    """ Take an ontology
    Return a list with all concept name of this ontology
    ontology is created by the function load ontology """

    list_concept = []
    # We collect all
    for concept in ontology.classes():
        print(concept.name)
        list_concept.append(concept.name)
    return list_concept


def load_ontology(ontology_path, ontology_name):  # ontology_name
    """ Take the ontology path and ontology name and return the ontolgy
    CARE the ontolgy path must be ABSOLUTE ! """
    # list_ontologies = os.listdir(ontology_path)
    onto_path.append(ontology_path)
    ontology = get_ontology(ontology_name).load()
    return ontology



def onto_main(config_file):
    """Main function"""

    config = load_config(config_file)
    ontology_path = config['ontologies']['path']

    for ontology_name in os.listdir(ontology_path):
        ontology = load_ontology(ontology_path, ontology_name)
        list_concept = return_concept_name(ontology)
        # print(list_concept)


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
