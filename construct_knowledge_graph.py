#! /usr/bin/env python3

import json
import yaml
import rdflib
import os
import extract_abstract as ex_ab

def load_config(config_file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config


def create_rdf_graph(directory):
    """Take a directory with all files in an xml format
    and convert it in a n3 format"""

    rdf_graph = rdflib.Graph()

    for file_name in os.listdir(directory):
        path_name = '{}{}'.format(directory, file_name)
        #rdf_graph.parse
        print(path_name)
        rdf_graph.parse(path_name, format="xml")

    #s = rdf_graph.serialize(format='n3')
    #print(s.decode("utf-8") )


    for subj, pred, obj in rdf_graph:
       if (subj, pred, obj) not in rdf_graph:
           raise Exception("It better be!")
       else:
           print('{} {} {}'.format(subj,pred,obj))

if __name__ == '__main__':
    """
    g = rdflib.Graph()
    result = g.parse("http://www.w3.org/People/Berners-Lee/card")

    print("graph has %s statements." % len(g))
    # prints graph has 79 statements.

    for subj, pred, obj in g:
       if (subj, pred, obj) not in g:
           raise Exception("It better be!")
       #else:
    #       print('{} {} {}'.format(subj,pred,obj))

    s = g.serialize(format='n3')

    print(type(s))
    print(s.decode("utf-8") )"""

    #config = load_config('config/config_rdf.yml')
    #create_rdf_graph(config['content_directory'])

    config_abstract = 'config/config_extract.yml'
    for lol1, lol2 in ex_ab.extract_abstracts(config_abstract):
        print('{}\n{}'.format(lol1,lol2))
