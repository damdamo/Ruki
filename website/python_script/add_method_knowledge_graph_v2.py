#! /usr/bin/env python3

import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, RDFS
from random import randint
#import python_script.generic_functions as gf
import generic_functions as gf
import re
import os.path
import sys
import json


def extract_json_to_dic(file_name):
    """Take a json file and return a dictionnary"""
    json_file = open(file_name)
    json_str = json_file.read()
    json_dic = json.loads(json_str)

    return json_dic

def extract_yml_to_dic(file_name):
    """Take a yml file and return a dictionnary"""
    yml_dic = gf.load_config(file_name)
    return yml_dic

def parse_file_to_dic(file_name):
    """Parse file take a file and return a dictionnary
    This function allow to choose the good format that we have
    in input
    """
    dic_file = {}
    extension = os.path.splitext(file_name)[1]
    if extension == '.json':
        dic_file = extract_json_to_dic(file_name)

    elif extension == '.yml':
        dic_file = extract_yml_to_dic(file_name)
    else:
        sys.exit('Format file isn\'t supported.\nFormat are: .json / .yml')
    return dic_file

def dic_to_rdf(dic, rdf_graph, name):
    """dic_to_rdf is a function which takes a dictionnary
    and transform it into rdf. """

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    cui = Namespace('http://cui.unige.ch/')


    for el in dic['objects']:
        cluster = dic['objects'][el]
        if cluster['type'] == 'cluster':
            rdf_graph.add((cui[el], RDFS.subClassOf, SKOS.Concept))
            rdf_graph.add((cui[el], SKOS.inSchema, cui[name]))
            rdf_graph.add((cui[el], SKOS.prefLabel, Literal(cluster['name'])))

    for el in dic['relations']:
        relation = dic['relations'][el]
        if (relation['type']).lower() == 'subtypeof':
            rdf_graph.add((cui[relation['domain']], RDFS.subClassOf, cui[relation['range']]))

        elif (relation['type']).lower() == 'belongto':
            index_name = '{}_{}'.format(el, randint(1000,9999))
            blank_node = BNode(index_name)
            rdf_graph.add((blank_node, RDF.type, cui.art_concept_link))
            rdf_graph.add((blank_node, cui.has_article, vgiid[str(relation['domain'])]))
            rdf_graph.add((blank_node, cui.has_concept, cui[relation['range']]))


def create_rdf_graph(file_name, output_file):
    """Take the config in a dictionnary and use it to create an rdf graph"""

    dic_file = parse_file_to_dic(file_name)
    rdf_graph = gf.basic_knowledge_graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    cui = Namespace('http://cui.unige.ch/')

    if 'method_name' in dic_file:
        # We give a name for the kernel
        # We add rng to avoid same name
        # for different method
        # nb_alea = randint(1000,9999)
        # name = '{}_{}'.format(dic_file['method_name'][0:15].replace(' ','_'), nb_alea)
        name = '{}'.format(dic_file['method_name'][0:15].replace(' ','_'))
        rdf_graph.add((cui[name], RDF.type, cui.knowledge_extractor_result))
        rdf_graph.add((cui[name], SKOS.prefLabel, Literal(dic_file['method_name'])))

    else:
        return 'error'

    # If we have informations we add it
    if 'method_informations' in dic_file:
        rdf_graph.add((cui[name], SKOS.note, Literal(dic_file['method_informations'])))
    else:
        return 'error'

    rdf_graph.add((cui[name], RDFS.subClassOf, SKOS.ConceptScheme))
    rdf_graph.add((SKOS.Concept, RDFS.subClassOf, SKOS.ConceptScheme))

    # We call function to complete our knowledge graph
    dic_to_rdf(dic_file, rdf_graph, name)

    rdf_normalized = rdf_graph.serialize(format='n3')
    rdf_normalized = rdf_normalized.decode('utf-8')
    print(rdf_normalized)

    #gf.write_rdf(output_file, rdf_normalized)

    return [rdf_normalized, name]

if __name__ == '__main__':

    config = gf.load_config('config/config_add_method_knowledge_graph.yml')
    create_rdf_graph('newFormat.yml', 'lol.txt')
