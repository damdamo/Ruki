#! /usr/bin/env python3

import json
import yaml
import rdflib

def create_rdf_graph(directory):
    """Take a directory with all files in an xml format
    and convert it in a n3 format"""

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

    g = rdflib.Graph()
    g.parse("Results/Extracts/Multiple/766.xml", format="xml")
    len(g) # prints 2

    """
    s = g.serialize(format='n3')
    print(s.decode("utf-8") )
    """

    for subj, pred, obj in g:
       if (subj, pred, obj) not in g:
           raise Exception("It better be!")
       else:
           print('{} {} {}'.format(subj,pred,obj))
