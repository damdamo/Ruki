#! /usr/bin/env python3

from owlready2 import *
import os
import yaml
from nltk.corpus import stopwords
import time


def load_config(file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config


def load_ontology(ontology_path, ontology_name):  # ontology_name
    """ Take the ontology path and ontology name and return the ontolgy
    CARE the ontolgy path must be ABSOLUTE ! """
    # list_ontologies = os.listdir(ontology_path)
    onto_path.append(ontology_path)
    ontology = get_ontology(ontology_name).load()
    return ontology


def return_concept_name(ontology):
    """ Take an ontology
    Return a list with all concept name of this ontology
    ontology is created by the function load ontology """

    # We create a list to put our concepts
    list_concept = []

    for concept in ontology.classes():
        # We replace underscore by a space
        concept_name_clean = clean_concept_name(concept.name)
        # We add our concept into the list
        list_concept.append(concept_name_clean)

    return list_concept


def clean_concept_name(concept_name):
    """clean_concept_name can clean and normalized concept of the list_concept
    In this function we:
    - Replace underscore by a space
    - Replace all uppercase by lowercase """

    concept_name_normalized = concept_name.replace('_', ' ')
    concept_name_normalized = concept_name_normalized.lower()

    return concept_name_normalized

def clean_abstract(abstract):
    """clean_abstract can clean and normalized abstract
    In this function we:
    - Replace all uppercase by lowercase
    - Delete stopwords"""
    abstract_clean = abstract.lower()
    # We clean all stopwords with list of nltk
    abstract_clean = [word for word in abstract_clean.split() if word not in stopwords.words('english')]
    return abstract_clean


def find_concept_abstract(concept_dic, abstract_folder):
    """Take the dictionnary with concept and a folder with
    all abstracts.
    Return a new dictionnary where we count for each ontology
    the number of time where a concept appear
    Format: dic = {'onto1':{'abstract1':{'concept1': nb_occurence},...},...}
    """

    dic_concept_abstract = {}
    list_abstract_file = os.listdir(abstract_folder)

    i = 0

    for ontology in concept_dic:
        dic_concept_abstract[ontology] = {}
        for abstract_file in list_abstract_file:
            dic_concept_abstract[ontology][abstract_file] = {}
            file_name = '{}{}'.format(abstract_folder, abstract_file)
            with open(file_name, 'r') as output_file:
                for concept in concept_dic[ontology]:
                    abstract = output_file.read()
                    abstract_clean = clean_abstract(abstract)
                    dic_concept_abstract[ontology][abstract_file][concept] = abstract_clean.count(concept)
                    i = i + 1

    print(dic_concept_abstract['onto1_correct'])


def extract_onto_concepts(config_file):
    """Main function"""

    config = load_config(config_file)
    ontology_path = config['ontologies']['path']
    abstract_folder = config['abstract_folder']

    # We create a dic where for each ontology we create
    # a key which contains all concepts for this ontology
    concept_dic = {}

    for ontology_name in os.listdir(ontology_path):
        ontology = load_ontology(ontology_path, ontology_name)
        list_concept = return_concept_name(ontology)
        concept_dic[ontology.name] = list_concept

    find_concept_abstract(concept_dic, abstract_folder)


if __name__ == '__main__':

    # load file configuration
    config_file = 'config/config_ontologies.yml'
    extract_onto_concepts(config_file)

    """
    onto_path.append('/home/damien/Workspace/master_project/data/ontologies')
    # onto = get_ontology('kr-owlxml.owl')
    onto = get_ontology('onto1_correct.owl')
    onto.load()

    for item in onto.classes():
        print(item)

    """
