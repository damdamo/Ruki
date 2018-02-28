#! /usr/bin/env python3

import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, RDFS
from random import randint
import extract_abstract as ex_ab
import generic_functions as gf
import re


def extract_options(line):
    """Take a line and extract options to add
    informations. We have special tag for this like
    method_name, informations..."""

    # dic_options contains all options
    dic_options = {}

    for option in line.split('||'):
        if len(option) > 0:
            option_split = option.split('|')
            if len(option_split) > 1:
                if '\n' in option_split[1]:
                    option_split[1] = option_split[1].replace('\n', '')
                dic_options[option_split[0]] = option_split[1]

    return dic_options


def parse_file(file_name):
    """This method can parse the file with all data
    that you obtain with your method
    The format of input file must be a text file
    where each line is a set of article id
    All article id on a same line is in the same cluster"""

    # Contains all informations that we parse
    dic_informations = {}
    options = []

    # We give an id for every cluster
    cluster_count = 0
    first_line = True

    with open(file_name, 'r') as file_reading:
        for line in file_reading:
            if first_line and line[0:2]=='||':
                options = extract_options(line)
                first_line = False
            else:
                dic_informations[cluster_count] = []
                for element in line.split():
                    dic_informations[cluster_count].append(element)
                cluster_count = cluster_count + 1

    return dic_informations, options


def create_rdf_graph(config):

    config = gf.load_config('config/config_add_method_knowledge_graph.yml')
    file_name = config['informations_to_add']
    output_file = config['output_file']

    dic_informations, options = parse_file(file_name)

    rdf_graph = gf.basic_knowledge_graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    cui = Namespace('http://cui.unige.ch/')


    if 'method_name' in options:
        # We give a name for the kernel
        # We add rng to avoid same name
        # for different method
        nb_alea = randint(1000,9999)
        name = '{}_{}'.format(options['method_name'][0:6].replace(' ','_'), nb_alea)
        rdf_graph.add((cui[name], RDF.type, cui.knowledge_extractor_result))
        rdf_graph.add((cui[name], SKOS.prefLabel, Literal(options['method_name'])))
    else:
        # If we don't have a method name, we just generate a big
        # number for the name
        nb_alea = randint(10000,99999)
        name = '{}'.format(nb_alea)
        rdf_graph.add((cui[name], RDF.type, cui.knowledge_extractor_result))

    # If we have informations we add it
    if 'method_informations' in options:
        rdf_graph.add((cui[name], SKOS.note, Literal(options['method_informations'])))

    rdf_graph.add((cui[name], RDFS.subClassOf, SKOS.ConceptScheme))

    for i in range(0,len(dic_informations)-1):
        concept_name = 'concept_{}_{}'.format(i, name)
        rdf_graph.add((cui[concept_name], RDFS.subClassOf, SKOS.Concept))
        rdf_graph.add((cui[concept_name], SKOS.inSchema, cui[name]))
        # rdf_graph.add((cui[concept_name], SKOS.prefLabel, Literal(concept)))
        for article in dic_informations[i]:
            print('article ' + article)
            index_name = 'index_{}_{}'.format(i, article)
            rdf_graph.add((cui[index_name], RDF.type, cui.art_concept_link))
            rdf_graph.add((cui[index_name], cui.has_concept, cui[concept_name]))
            rdf_graph.add((cui[index_name], cui.has_article, vgiid[article]))

    rdf_normalized = rdf_graph.serialize(format='n3')
    rdf_normalized = rdf_normalized.decode('utf-8')

    # print(rdf_normalized)

    gf.write_rdf(output_file, rdf_normalized)

    return rdf_normalized

if __name__ == '__main__':

    config = gf.load_config('config/config_add_method_knowledge_graph.yml')
    create_rdf_graph(config)
