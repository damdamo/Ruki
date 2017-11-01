#! /usr/bin/env python3

import requests
import json
import yaml
import re


def load_config(file):
    # Load the config file
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config


def write_string_into_file(file_name, my_string):
    # Take a string and write it into a file
    with open(file_name, 'w') as output_file:
        output = '{}\n'.format(my_string)
        output_file.write("{}".format(output))


def get_page_id(dic):
    # Find id of a page and get it
    list_article = dic['categorymembers']
    list_id = []
    for element in list_article:
        list_id.append(element['pageid'])
    return list_id


def get_all_page_id(url, parameters_id):
    # Get all page id from all articles
    list_id = []
    # We obtain all id page
    for element in query(url, parameters_id):
        list_id = list_id + get_page_id(element)
    return list_id


def get_abstract(id, parameters_extract_content):
    # Get abstract from a specific page
    param = parameters_extract_content.copy()
    param['pageids'] = id

    for element in query(url, param):
        content = element['pages'][id]['revisions'][0]['*']
        # We clear all line break (need for regex)
        content = content.replace('\n', ' ')

    # Regex allow to keep only abstract
    regex_pattern = re.compile(config['regex']['get_abstract'])
    abstract = re.sub(regex_pattern, '', content)
    return abstract


def get_all_abstract(list_all_id, parameters_extract_content):
    # Collect all abstract


def query(url, request):
    request['action'] = 'query'
    request['format'] = 'json'
    lastContinue = {}
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the
        # last result.
        req.update(lastContinue)
        # Call API
        result = requests.get(url, params=req).json()
        if 'error' in result:
            raise Error(result['error'])
        if 'warnings' in result:
            print(result['warnings'])
        if 'query' in result:
            yield result['query']
        if 'continue' not in result:
            break
        lastContinue = result['continue']


if __name__ == '__main__':

    # url_to_extract = "http://vgibox.eu/repository/api.php?action=query&list=categorymembers&cmtitle=Category:VGI_Domain&format=json&continue="
    # Exemple d'url pour récupérer la page par l'id
    # http://vgibox.eu/repository/index.php?curid=919

    # load file configuration
    config_file = 'config.yml'
    config = load_config(config_file)

    # We extract id from articles
    parameters_id = config['parameters_id']
    url = config['url']

    # We collect all id
    list_all_id = get_all_page_id(url, parameters_id)

    parameters_extract_content = config['parameters_extract_content']
    get_abstract('687', parameters_extract_content)

    # Write an abstract into a file
    output = config['output']['file']
    write_string_into_file(output, abstract)
