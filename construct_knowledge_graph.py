#! /usr/bin/env python3

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF
import extract_abstract as ex_ab
import generic_functions as gf


def write_rdf(file_name, rdf):
    """A simple function to write rdf in a file"""
    with open(file_name, 'w') as output_file:
        output = '{}'.format(rdf)
        output_file.write("{}".format(output))


def create_rdf_graph(config):
    """Take a directory with all files in an xml format
    and convert it in a n3 format"""

    rdf_graph = Graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    my_namespace = Namespace('http://cui.unige.ch/')

    rdf_graph.bind("vgiid", vgiid)
    rdf_graph.bind("foaf", FOAF)
    rdf_graph.bind("dc", DC)

    config_abstract = 'config/config_extract.yml'

    for doc_id, dic_content in ex_ab.extract_abstracts(config_abstract):
        title = dic_content[doc_id]['title']
        description = dic_content[doc_id]['abstract']
        rdf_graph.add((vgiid[doc_id], RDF.type, my_namespace.article))
        rdf_graph.add((vgiid[doc_id], DC['title'], Literal(title)))
        rdf_graph.add((vgiid[doc_id], DC['description'], Literal(description)))

        for keyword in dic_content[doc_id]['keywords'].split():
            print(keyword)
            rdf_graph.add((vgiid[doc_id], DC['keywords'], Literal(keyword)))

    rdf_normalized = rdf_graph.serialize(format='n3')
    rdf_normalized = rdf_normalized.decode("utf-8")

    write_rdf(config['rdf_file'], rdf_normalized)


if __name__ == '__main__':

    config = gf.load_config('config/config_rdf.yml')
    create_rdf_graph(config)

    """config_abstract = 'config/config_extract.yml'
    for lol1, lol2 in ex_ab.extract_abstracts(config_abstract):
        print('{}\n{}'.format(lol1,lol2))"""
