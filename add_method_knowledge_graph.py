#! /usr/bin/env python3

import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF
import extract_abstract as ex_ab
import generic_functions as gf

def write_rdf(file_name, rdf):
    """A simple function to write rdf in a file"""
    with open(file_name, 'w') as output_file:
        output = '{}'.format(rdf)
        output_file.write("{}".format(output))

def parse_file(file_name):
    """This method can parse the file with all data
    that you obtain with your method
    The format of input file must be a text file
    where each line is a set of article id
    All article id on a same line is in the same cluster"""

    # Contains all informations that we parse
    dic_informations = {}

    # We give an id for every cluster
    cluster_count = 0

    with open(file_name, 'r') as file_reading:
        for line in file_reading:
            dic_informations[cluster_count] = []
            for element in line.split():
                dic_informations[cluster_count].append(element)
            cluster_count = cluster_count + 1

    return dic_informations

def construct_knowledge_graph():
    pass

if __name__ == '__main__':

    config = gf.load_config('config/config_add_method_knowledge_graph.yml')
    file_name = config['informations_to_add']
    parse_file(file_name)
