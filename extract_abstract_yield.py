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


def write_abstract_into_file(file_name, abstract):
    # Take a string and write it into a file
    with open(file_name, 'a') as output_file:
        print(abstract)
        output = '{}\n'.format(abstract)
        output_file.write("{}".format(output))


def get_page_id(dic):
    # Find id of a page and return it in a string type
    list_article = dic['categorymembers']
    for element in list_article:
        yield str(element['pageid'])


def get_all_page_id(url, parameters_id):
    # Get all page id from all articles
    list_id = []
    # We obtain all id page
    for element in query(url, parameters_id):
        yield get_page_id(element)


def get_abstract(gen_id, parameters_extract_content):
    # Get abstract from a specific page
    # More a test function
    param = parameters_extract_content.copy()

    for my_id in gen_id:
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
    for gen_id in list_all_id:
        for my_id in gen_id:
            parameters_extract_content['pageids'] = my_id
            for element in query(url, parameters_extract_content):
                content = element['pages'][my_id]['revisions'][0]['*']
                # We clear all line break (need for regex)
                content = content.replace('\n', ' ')

            # Regex allow to keep only abstract
            regex_pattern = re.compile(config['regex']['get_abstract'])
            abstract = re.sub(regex_pattern, '', content)
            yield abstract


def query(url, request):
    request['action'] = 'query'
    request['format'] = 'json'
    last_continue = {}
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the
        # last result.
        req.update(last_continue)
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
        last_continue = result['continue']


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
    # get_abstract('687', parameters_extract_content)

    i = 0
    for abstract in get_all_abstract(list_all_id, parameters_extract_content):
        print(i)
        write_abstract_into_file(config['output']['file'], abstract)
        i = i + 1

    # Write an abstract into a file
    # output = config['output']['file']
    # write_string_into_file(output, abstract)
