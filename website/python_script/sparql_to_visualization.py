#! /usr/bin/env python3

import requests
import python_script.generic_functions as gf
# import generic_functions as gf
import csv
import json
import time
from nltk.corpus import stopwords
import textwrap
from urllib.parse import urlparse


URL_SERVER = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien'
NB_MAX_ARTICLE = 10

def clean_stop_words(sentence):
    """We clean all stop words in a sentence"""
    sentence_clean = ' '.join([word for word in sentence.split(
    ) if word not in stopwords.words('english')])
    return sentence_clean

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
          ?concepts skos:inSchema cui:%s.
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

def get_all_articles():
    """Return a json file with all informations about articles"""
    query_base =  """
        SELECT DISTINCT (str(?article) as ?url) ?title (group_concat(?keyword ; separator="; ") as ?keywords) ?abstract
        WHERE {
              ?article rdf:type schema:Article.
              ?article dc:title ?title.
              OPTIONAL{?article dc:subject ?keyword}
              OPTIONAL{?article dc:description ?abstract}
        } GROUP BY ?article ?title ?abstract
    """

    query = add_prefix_sparql_request(query_base)

    answer = get_response_sparql(query)
    dic = {}

    for article in answer['results']['bindings']:

        url = article['url']['value']
        url_decomposed = urlparse(url)
        article_id = (url_decomposed.query).replace('curid=', '')

        dic[url] = {}

        dic[url]['id'] = article_id
        dic[url]['title'] = article['title']['value']

        if len(article['keywords']['value']) != 0:
            dic[url]['keywords'] = article['keywords']['value']

        if len(article['abstract']['value']) != 0:
            dic[url]['abstract'] = article['abstract']['value']

    data_json = json.dumps(dic, indent=1, ensure_ascii=False)
    name_file = 'articles.json'
    upload_folder = 'temp'
    complete_path = '{}/{}'.format(upload_folder, name_file)

    with open(name_file, 'w') as nf:
        nf.write(data_json)

    return name_file


def get_articles(concept_uri):
    """Give us a list of article which is link for a specific
    concept. We return a list of dictionnary where each dic contain his informations"""

    query_base =  """
        SELECT DISTINCT (str(?article) as ?url) ?title (group_concat(?keyword ; separator="; ") as ?keywords) ?abstract
        WHERE {
            ?a cui:has_concept <%s>.
            ?a cui:has_article ?article.
            ?article dc:title ?title.
            OPTIONAL{?article dc:subject ?keyword}
            OPTIONAL{?article dc:description ?abstract}
        } GROUP BY ?article ?title ?abstract
    """ % (concept_uri)

    query = add_prefix_sparql_request(query_base)

    answer = get_response_sparql(query)

    list_articles = []

    if 'title' not in answer['results']['bindings'][0]:
        return []

    for article in answer['results']['bindings']:
        """dic = {}
        dic['name'] = article['title']['value'][0:20]
        dic['children'] = []

        dic_temp = {}
        dic_temp['size'] = 1

        dic_temp['title'] = 'Title: {}'.format(article['title']['value'][0:30])

        dic_temp['url'] = article['url']['value']

        if len(article['keywords']['value']) != 0:
            keywords = 'Keywords: {}'.format(article['keywords']['value'][0:60])
            dic_temp['keywords'] = keywords

        if len(article['abstract']['value']) != 0:
            abstract = 'Abstract: {}'.format(article['abstract']['value'][0:90])
            dic_temp['abstract'] = abstract

        dic['children'].append(dic_temp)
        list_articles.append(dic)"""

        dic = {}
        dic['name'] = article['title']['value'][0:20]
        dic['size'] = 1
        # dic['title'] = 'Title: {}'.format(article['title']['value'][0:30])
        dic['title'] = '{}'.format(article['title']['value'])

        dic['url'] = article['url']['value']

        if len(article['keywords']['value']) != 0:
            # keywords = 'Keywords: {}'.format(article['keywords']['value'][0:60])
            keywords = '{}'.format(article['keywords']['value'][0:100])
            dic['keywords'] = keywords

        if len(article['abstract']['value']) != 0:
            # abstract = 'Abstract: {}'.format(article['abstract']['value'][0:90])
            abstract = '{}'.format(article['abstract']['value'][0:150])

            dic['abstract'] = abstract

        list_articles.append(dic)

    if len(list_articles) > NB_MAX_ARTICLE:
        return []
    else:
        return list_articles


def explore_recursive(method_name, root_uri, root_name):
    """"This function is the main part of the code. It's a recursive
    function which is used to recreate the hierarchy of the knowledge graph
    and put article in different categories if it exists.
    method_name is the name of your method (same name that we give in the json file)
    It's needed for questionning our sparql database"""
    dic = {}
    # We keep only pertinent information
    name_temp = clean_stop_words(root_name.lower())
    dic['name'] = (name_temp[0:20]).capitalize()
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
            if root_name != el['name']:
                #print('root name = ' + root_name)
                #print('sous concept = ' + el['name'])
                list_rec = [explore_recursive(method_name, el['concepts'], el['name'])]
                dic['children'] = dic['children'] + list_rec
            dic['children'] = dic['children'] + get_articles(root_uri)

        while '' in dic['children']:
            dic['children'].remove('')
        while {} in dic['children']:
            dic['children'].remove({})

        if len(dic['children']) == 0:
            return {}

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
    """We put a method and create a json file to use it later by
    our vizualisation"""
    # method_name = config['method_name']
    # root = 'owl:Thing

    # root = 'http://www.w3.org/2002/07/owl#Thing'
    root = 'http://cui.unige.ch/root'

    dic = {}
    res = explore_recursive(method_name, root, 'root')

    data_json = json.dumps(res, indent=1, ensure_ascii=False)
    name_file = 'static/method_schema/{}.json'.format(method_name)

    with open(name_file, 'w') as nf:
        nf.write(data_json)


if __name__ == '__main__':

    config = gf.load_config('config/config_manage_sparql.yml')

    #write_informations_for_visualization('onto1_correct')
    write_informations_for_visualization('FCA-based clustering with pattern-mining as a preprocessing step')
    get_all_articles()
