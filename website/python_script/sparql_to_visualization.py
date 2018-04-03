#! /usr/bin/env python3

import requests
import python_script.generic_functions as gf
import csv
import json
import time

URL_SERVER = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien'


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

def get_list_method():
    """We make a sparl query to get all method that we have in our knowledge graph
    Return a list of string with all method name"""
    query_base = """SELECT DISTINCT ?name
                    WHERE {
                    	?onto rdf:type cui:knowledge_extractor_result.
                      	?onto skos:prefLabel ?name
                    }"""
    query = add_prefix_sparql_request(query_base)
    answer = get_response_sparql(query)

    list_method = []
    for method in answer['results']['bindings']:
        list_method.append(method['name']['value'])
    return list_method

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
            dic[key] = (val[key]['value'])[0:30]
        list_articles.append(dic)

    return list_articles

def explore_recursive(method_name, root_uri, root_name):

    dic = {}
    dic['name'] = root_name[0:20]
    dic['children'] = []
    print(dic['name'])

    if len(get_sub_concepts(method_name, root_uri)) == 0:

        dic['children'] = get_articles(root_uri)
        articles = get_articles(root_uri)
        if len(articles) != 0:
            dic['children'] = articles
        else:
            return ''

    else:
        for el in get_sub_concepts(method_name, root_uri):
            dic['children'] = dic['children'] + [explore_recursive(method_name, el['concepts'], el['name'])]
        dic['children'] = dic['children'] + get_articles(root_uri)

        while '' in dic['children']:
            dic['children'].remove('')

    return dic


def get_response_sparql(query):
    """ We get answer of the sparql query in a json format """
    headers = {'Accept': 'application/sparql-results+json'}
    payload = {'query': '{}'.format(query), 'queryLn':'SPARQL', 'infer':'false'}
    result = requests.get(URL_SERVER, params=payload, headers=headers)
    result_decode = (result.content).decode("utf-8")
    #result_decode = result_decode.split('\r\n')
    result_decode = json.loads(result_decode)
    return result_decode

def write_informations_for_visualization(method_name):
    """We get an answer in a csv format depends on our query"""
    # method_name = config['method_name']
    # root = 'owl:Thing

    #root = 'http://www.w3.org/2002/07/owl#Thing'
    root = 'http://cui.unige.ch/Root'

    dic = {}
    res = explore_recursive(method_name, root, 'root')

    data_json = json.dumps(res, indent=1, ensure_ascii=False)
    name_file = 'static/method_schema/{}.json'.format(method_name)

    with open(name_file, 'w') as nf:
        nf.write(data_json)


if __name__ == '__main__':

    config = gf.load_config('config/config_manage_sparql.yml')

    write_informations_for_visualization('onto1_correct')
    #write_informations_for_visualization('k-means_animals')
