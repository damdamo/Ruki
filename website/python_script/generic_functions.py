#! /usr/bin/env python3

import yaml
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, SKOS, RDFS

def load_config(config_file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config

def write_rdf(file_name, rdf_to_write):
    """ Take a string and write it into a file """
    # If we have multiple file we write on it
    with open(file_name, 'w') as output_file:
        output_file.write("{}".format(rdf_to_write))

def basic_knowledge_graph():
    """ Return the base of our knowledge graph with already
    the binding of namespace """
    rdf_graph = Graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    schema = Namespace('http://schema.org/')
    cui = Namespace('http://cui.unige.ch/')

    rdf_graph.bind("cui", cui)
    rdf_graph.bind("vgiid", vgiid)
    rdf_graph.bind("dc", DC)
    rdf_graph.bind("skos", SKOS)
    rdf_graph.bind("rdfs", RDFS)
    rdf_graph.bind("schema", schema)

    return rdf_graph
