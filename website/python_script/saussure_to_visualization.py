#! /usr/bin/env python3

import requests
#import python_script.generic_functions as gf
import generic_functions as gf
import csv
import json
import time
from nltk.corpus import stopwords
import textwrap
from urllib.parse import urlparse


URL_SERVER = 'http://ke.unige.ch:8080/rdf4j-server/repositories/fds'
NB_MAX_ARTICLE = 100

def clean_stop_words(sentence):
    """We clean all stop words in a sentence"""
    sentence_clean = ' '.join([word for word in sentence.split(
    ) if word not in stopwords.words('english')])
    return sentence_clean

def add_prefix_sparql_request(sparql_request):
    """Add the prefix for sparql request"""
    prefixes = '''PREFIX s: <http://saussure.com/ressource/>
                  PREFIX p: <http://saussure.com/property/>
                  '''
    query = '{}{}'.format(prefixes, sparql_request)
    return query

def get_dic_saussure():
    """We make a sparl query to get all informations about what Saussure wrote
    with the hierarchy which exists. We keep it into a dictionnary"""
    query_base = """
                    SELECT DISTINCT ?section ?box ?subdiv ?surf (group_concat(?text ; separator="; ") as ?page)
                    where {

                      ?section p:hasArchiveBox ?box.
                      ?box p:hasSubdivisions ?subdiv.
                      ?subdiv p:hasSurfaceEcriture ?surf.
                      ?surf p:hasPhoto/p:contient/p:hasTranscriptionElement/p:rawText ?text

                    } GROUP BY ?section ?box ?subdiv ?surf
                """
    query = add_prefix_sparql_request(query_base)
    answer = get_response_sparql(query)

    dic = {}
    for element in answer['results']['bindings']:
        section = clear_ressources(element['section']['value'])
        box = clear_ressources(element['box']['value'])
        subdiv = clear_ressources(element['subdiv']['value'])
        page = element['page']['value']

        if section not in dic:
            dic[section] = {}
        if box not in dic[section]:
            dic[section][box] = {}
        if subdiv not in dic[section][box]:
            dic[section][box][subdiv] = []

        #dic[section][box][subdiv].append({'abstract':page, 'size':1})
        dic[section][box][subdiv].append({'abstract':page, 'size':1, 'title':'titre', 'keywords':'kw', 'url':'url', 'name':'name'})


    return dic

def clear_ressources(r_string):
    prefix = 'http://saussure.com/ressource/'
    new_string = r_string.replace(prefix, '')
    return new_string

def convert_dic_to_flare_json(dic):
    "Take a dictionnary python and return the data into json flare format"

    new_dic = {}
    print(type(dic))

    if type(dic) is list:
        new_dic = dic
        print(new_dic)
        return new_dic

    list_dic = []
    for el in dic:
        list_dic.append({'name':el, 'children':convert_dic_to_flare_json(dic[el])})

    return list_dic


def get_response_sparql(query):
    """ We get answer of the sparql query in a json format """
    headers = {'Accept': 'application/sparql-results+json'}
    payload = {'query': '{}'.format(query), 'queryLn':'SPARQL', 'infer':'false'}
    result = requests.get(URL_SERVER, params=payload, headers=headers)
    result_decode = (result.content).decode("utf-8")
    #result_decode = result_decode.split('\r\n')
    result_decode = json.loads(result_decode)
    return result_decode


def write_informations_for_visualization(config):
    """We create the json file with flare style to print it in our visualization"""

    answer = get_dic_saussure()
    data_json = json.dumps(answer, indent=1, ensure_ascii=False)
    name_file = 'saussure_dic.json'

    with open(name_file, 'w') as nf:
        nf.write(data_json)

    json1_file = open('saussure_dic.json')
    json1_str = json1_file.read()
    json1_data = json.loads(json1_str)

    # We convert dic json data into flare json data
    flare_json = convert_dic_to_flare_json(json1_data)

    # We add a unique root to our visualization
    answer = {'name':'Root', 'children':flare_json}

    data_json = json.dumps(answer, indent=1, ensure_ascii=False)
    name_file = 'static/method_schema/saussure.json'

    with open(name_file, 'w') as nf:
        nf.write(data_json)



if __name__ == '__main__':

    config = gf.load_config('config/config_manage_sparql.yml')

    write_informations_for_visualization(config)
