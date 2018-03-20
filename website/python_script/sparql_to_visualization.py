#! /usr/bin/env python3

import requests
import generic_functions as gf
import csv

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
          ?concepts rdfs:subClassOf %s.
          ?concepts skos:prefLabel ?name.
        }
        ''' % (method_name, root_uri)

    query = add_prefix_sparql_request(query_base)
    answer = get_response_sparql(query)
    return answer

def find_articles(concept_uri):
    """Give us a list of article which is link for a specific
    concept. We return a csv/text with answer which is a list of article """

    query_base =  """
        SELECT DISTINCT ?article
        WHERE {
            ?a cui:has_concept %s.
            ?a cui:has_article ?article.
        }
    """ % (concept_uri)

    query = add_prefix_sparql_request(query_base)
    answer = get_response_sparql(query)
    return answer

def transform_csv_text_to_dic(csv_text):
    """Take a csv text (not file) and convert it in a dic"""

    csv_list = csv_text.split('\r\n')
    list_var = []

    nb_var = len(csv_list[0].split(','))
    for var in csv_list[0].split(','):
        list_var.append(var)

    dic = {}

    for element in csv_list:
        for i in range(nb_var):
            sub_dic = {}



def get_response_sparql(query):
    # headers = {'Accept': 'application/sparql-results+json'}
    payload = {'query': '{}'.format(query), 'queryLn':'SPARQL', 'infer':'false'}
    result = requests.get(url, params=payload)
    #print(result)
    #print(result.headers)
    result_decode = (result.content).decode("utf-8")
    return result_decode

def get_informations_for_visualization(config):
    """We get an answer in a csv format depends on our query"""
    url = config['url_server']
    method_name = config['method_name']
    root = 'owl:Thing'

    infos = get_sub_concepts(method_name, root)
    print(transform_csv_text_to_dic(infos))

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
