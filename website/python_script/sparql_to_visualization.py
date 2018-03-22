#! /usr/bin/env python3

import requests
import generic_functions as gf
import csv
import json
import time

def add_prefix_sparql_request(sparql_request):
    """Add the prefix for sparql request"""
    prefixes = '''PREFIX cui: <http://cui.unige.ch/>
                PREFIX dc: <http://purl.org/dc/elements/1.1/>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX vgiid: <http://vgibox.eu/repository/index.php?curid=>
                PREFIX xml: <http://www.w3.org/XML/1998/namespace>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX schema: <http://schema.org/>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                '''
    query = '{}{}'.format(prefixes, sparql_request)
    return query

def get_sub_concepts(method_name, root_uri):
    """ Construct a sparql query with the method name and root name
    This query allow to get all concept sub class of root_uri in a specific
    method name. We need it to make a Depth-first search
    We return a csv/text which is a list of concepts with their name"""
    query_base = '''
        SELECT DISTINCT ?concepts ?name
        WHERE {
          ?method skos:prefLabel "%s".
          ?concepts skos:inSchema ?method.
          ?concepts rdfs:subClassOf <%s>.
          ?concepts skos:prefLabel ?name.
        }
        ''' % (method_name, root_uri)

    query = add_prefix_sparql_request(query_base)
    answer = get_response_sparql(query)

    list_articles = []

    for val in answer['results']['bindings']:
        dic = {}
        for key in val.keys():
            dic[key] = val[key]['value']
        list_articles.append(dic)

    return list_articles

def get_articles(concept_uri):
    """Give us a list of article which is link for a specific
    concept. We return a list of dictionnary where each dic contain his informations"""

    query_base =  """
        SELECT DISTINCT ?name
        WHERE {
            ?a cui:has_concept <%s>.
            ?a cui:has_article ?article.
            ?article dc:title ?name
        }
    """ % (concept_uri)

    query = add_prefix_sparql_request(query_base)
    answer = get_response_sparql(query)

    list_articles = []

    for val in answer['results']['bindings']:
        dic = {}
        dic['size'] = 1
        for key in val.keys():
            dic[key] = val[key]['value']
        list_articles.append(dic)

    return list_articles

def explore_recursive(method_name, root_uri, root_name):
    """Deux problèmes: Cas où on arrive sur une feuille sans article
    Autre problème avec append sur les feuilles ou il faudrait un + (concat)"""

    if len(get_sub_concepts(method_name, root_uri)) == 0:
        print('lol')
        return get_articles(root_uri)

    else:
        dic = {}
        dic['name'] = root_name
        dic['children'] = []
        list_articles = get_articles(root_uri)
        for el in get_sub_concepts(method_name, root_uri):
            print(el['name'])
            if len(get_sub_concepts(method_name, el['concepts'])) != 0:
                #print(len(get_sub_concepts(method_name, el['concepts'])))
                dic['children'] = dic['children'] + [explore_recursive(method_name, el['concepts'], el['name'])]
            else:
                if len(get_articles(el['concepts'])) != 0:
                    dic['children'] = dic['children'] + get_articles(el['concepts'])


        if len(list_articles) != 0:
            #print(get_articles(root_uri))
            dic['children'] = dic['children'] + get_articles(root_uri)

        if len(dic['children']) != 0:
            return dic

        return ''


def get_response_sparql(query):
    """ We get answer of the sparql query in a json format """
    headers = {'Accept': 'application/sparql-results+json'}
    payload = {'query': '{}'.format(query), 'queryLn':'SPARQL', 'infer':'false'}
    result = requests.get(url, params=payload, headers=headers)
    result_decode = (result.content).decode("utf-8")
    #result_decode = result_decode.split('\r\n')
    result_decode = json.loads(result_decode)
    return result_decode

def get_informations_for_visualization(config):
    """We get an answer in a csv format depends on our query"""
    url = config['url_server']
    method_name = config['method_name']
    # root = 'owl:Thing'
    root = 'http://www.w3.org/2002/07/owl#Thing'

    dic = {}
    res = explore_recursive(method_name, root, 'root')

    # print(res)

    monjson = json.dumps(res, indent=1, ensure_ascii=False)

    with open('lol.json', 'w') as lol:
        lol.write(monjson)


if __name__ == '__main__':

    config = gf.load_config('config/config_manage_sparql.yml')

    url = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien'

    get_informations_for_visualization(config)


"""
    SELECT DISTINCT ?method ?concepts ?article
    WHERE {
      ?method skos:prefLabel "onto1_correct".
      ?concepts skos:inSchema ?method.
      ?concepts rdfs:subClassOf owl:Thing.
      ?a cui:has_concept ?concepts.
      ?a cui:has_article ?article.
    }
"""
