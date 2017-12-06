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


def create_rdf_graph(config):
    """Take a directory with all files in an xml format
    and convert it in a n3 format"""

    rdf_graph = Graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    cui = Namespace('http://cui.unige.ch/')

    rdf_graph.bind("vgiid", vgiid)
    rdf_graph.bind("foaf", FOAF)
    rdf_graph.bind("dc", DC)
    rdf_graph.bind("cui", cui)

    config_abstract = 'config/config_extract.yml'

    for doc_id, dic_content in ex_ab.extract_abstracts(config_abstract):
        title = dic_content[doc_id]['title']
        description = dic_content[doc_id]['abstract']
        rdf_graph.add((vgiid[doc_id], RDF.type, cui.article))
        rdf_graph.add((vgiid[doc_id], DC['title'], Literal(title)))
        rdf_graph.add((vgiid[doc_id], DC['description'], Literal(description)))

        for keyword in dic_content[doc_id]['keywords']:
            rdf_graph.add((vgiid[doc_id], DC['subject'], Literal(keyword)))

    rdf_normalized = rdf_graph.serialize(format='n3')
    rdf_normalized = rdf_normalized.decode('utf-8')

    if config['rdf']['write_rdf']:
        write_rdf(config['rdf']['file_name'], rdf_normalized)

def query_example():
    """Just to keep an example query, not for using"""
    rdf_graph = Graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    cui = Namespace('http://cui.unige.ch/')

    rdf_graph.bind("vgiid", vgiid)
    rdf_graph.bind("foaf", FOAF)
    rdf_graph.bind("dc", DC)
    rdf_graph.bind("cui", cui)
    rdf_graph.add((vgiid['919'], RDF.type , cui.article))

    qres = rdf_graph.query(
    """
    PREFIX cui:<http://cui.unige.ch/>
    SELECT DISTINCT ?a
       WHERE {
          ?a a cui:article .
       }""")

    for row in qres:
        print(row)

def merge_graph(rdf_file1, rdf_file2):
    """Merge graph can merge two rdf files
    rdf_file1: Just the path of rdf_file1
    rdf_file2: Same for rdf_file2
    Output the merge of two rdf"""

    rdf_graph.parse(rdf_file1, format='n3')
    rdf_graph.parse(rdf_file2, format='n3')

    # For printing
    # rdf_normalized = rdf_graph.serialize(format='n3')
    # rdf_normalized = rdf_normalized.decode('utf-8')

    return rdf_graph

if __name__ == '__main__':

    config = gf.load_config('config/config_rdf.yml')
    create_rdf_graph(config)

    """config_abstract = 'config/config_extract.yml'
    for lol1, lol2 in ex_ab.extract_abstracts(config_abstract):
        print('{}\n{}'.format(lol1,lol2))"""
