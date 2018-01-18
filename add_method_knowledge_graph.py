#! /usr/bin/env python3

import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF
import extract_abstract as ex_ab
import generic_functions as gf
import re

def write_rdf(file_name, rdf):
    """A simple function to write rdf in a file"""
    with open(file_name, 'w') as output_file:
        output = '{}'.format(rdf)
        output_file.write("{}".format(output))

def extract_options(line):
    """Take a line and extract options to add
    informations. We have special tag for this like
    method_name, informations..."""

    method_name = extract_tag('method_name', line)
    method_informations = extract_tag('method_informations', line)

    dic = {}

    print(method_name)
    print(method_informations)


    # method_name = line[pos_method_name[0], pos_method_name[1]]
    # method_informations = line[pos_method_informations[0], pos_method_informations[1]]

    #regex_get_abstract = re.compile('{(.)*}( )?')
    #abstract = re.sub(regex_get_abstract, '', content_mod)

def extract_tag(tag_name, line):
    """Allow to extract a tag for extract_options
    """

    # Method to keep our tags with regex
    pattern_name = re.compile(tag_name + "( )?=( )?{(.)*}")
    content = re.search(pattern_name, line)
    final_tag = ''

    if content is not None:
        pos = content.span()
        final_tag = line[pos[0]:pos[1]]

    return final_tag


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
    first_line = True

    with open(file_name, 'r') as file_reading:
        for line in file_reading:
            if first_line and line[0:1]=='\\':
                extract_options(line)
                first_line = False
            else:
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
