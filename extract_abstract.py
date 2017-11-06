#! /usr/bin/env python3

import requests
import json
import yaml
import re


def load_config(file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config


def query(url, request):
    """ Allow to make a query and collect informations about page
    In our case we use it to have id from publications"""
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


def write_abstract_into_file(file_name, abstract):
    """ Take a string and write it into a file """
    with open(file_name, 'a') as output_file:
        if abstract != '':
            output = '{}\n'.format(abstract)
            output_file.write("{}".format(output))


def get_page_id(dic):
    """ Find id of a page and return it in a string type """
    list_article = dic['categorymembers']
    for element in list_article:
        yield str(element['pageid'])


def get_all_page_id(url, parameters_id):
    """ Get all page id from all articles """
    list_id = []
    # We obtain all id page
    for element in query(url, parameters_id):
        yield get_page_id(element)


def clean_abstract(abstract):
    """ Allow to remove useless component in the abstract
    like link. Regex can clean link and square roots """
    regex_link = re.compile(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    regex_square_bracket = re.compile('[\[\]]')
    clean_abstract = re.sub(regex_link, '', abstract)
    clean_abstract = re.sub(regex_square_bracket, '', clean_abstract)
    return clean_abstract

def get_keywords(content):
    """ Collect all keywords from content with parsing"""
    regex_get_keywords = re.compile('Keywords=(.)*\n')
    keywords = regex_get_keywords.search(content)

    # We verify that keywords exist
    if keywords is not None:
        keywords = keywords.group(0)
        print(keywords)
        #We keep only keywords
        keywords = keywords.replace('Keywords=', '')
        table_keywords = keywords.split(',')
        # There is an empty word because the format of data is like:
        # Keywords= k1, k2, k3, (with a comma at the end)
        # So we suppress the last word of the list which is empty
        table_keywords.pop()
        return table_keywords

    # If there are any keywords, we return an empty table
    return []


def get_abstract_from_content(content, options):
    """ Get abstract from a content of a specific page """
    # We clear all line break (need for regex)
    content_mod = content.replace('\n', ' ')

    # Option to keep keywords
    if options['keywords']:
        table_keywords = get_keywords(content)
        regex_get_abstract = re.compile('{(.)*}')
        abstract = re.sub(regex_get_abstract, '', content_mod)

        if options['xml']:
            abstract = '<sentences>' + abstract + '</sentences>'
            keywords_xml = ''
            for keyword in table_keywords:
                keywords_xml = keywords_xml + '<keyword>' + keyword + '</keyword>'
            abstract = keywords_xml + '\n' + abstract
        else:
            abstract = keywords + '\n' + abstract

    else:
        regex_get_abstract = re.compile('{(.)*}')
        abstract = re.sub(regex_get_abstract, '', content_mod)
        if options['xml']:
            abstract = '<sentences>' + abstract + '</sentences>'

    return clean_abstract(abstract)


def get_all_abstract(url, list_all_id, parameters_extract_content, options):
    """ Collect all abstract """
    for gen_id in list_all_id:
        for my_id in gen_id:
            parameters_extract_content['pageids'] = my_id
            for element in query(url, parameters_extract_content):
                content = element['pages'][my_id]['revisions'][0]['*']
                if options['title']:
                    if options['xml']:
                        content = '<title>' + element['pages'][my_id]['title'] + '</title>\n' + content
                    else:
                        content = element['pages'][my_id]['title'] + '\n' + content
            yield my_id, get_abstract_from_content(content, options)


def extract_abstracts(config_file):
    """ Extract all abstract of all Publication in the website
    and put it in a single file or multiple files. It depends
    options in the file config """

    config = load_config(config_file)

    # We extract id from articles
    parameters_id = config['parameters_id']
    url = config['url']

    # We collect all id
    list_all_id = get_all_page_id(url, parameters_id)

    parameters_extract_content = config['parameters_extract_content']

    # An indicator to know where we are in the process
    i = 0

    if config['options']['xml']:
        file_extension = '.xml'
    else:
        file_extension = '.txt'

    if not config['options']['multiple_file']:
        for _, abstract in get_all_abstract(url, list_all_id, parameters_extract_content, config['options']):
            print(i)
            name_file = config['output']['file'] + file_extension
            write_abstract_into_file(name_file, abstract)
            i = i + 1
    else:
        for doc_id, abstract in get_all_abstract(url, list_all_id, parameters_extract_content, config['options']):
            print(i)
            name_file = config['output']['folder'] + doc_id + file_extension
            write_abstract_into_file(name_file, abstract)
            i = i + 1


if __name__ == '__main__':

    # url_to_extract = "http://vgibox.eu/repository/api.php?action=query&list=categorymembers&cmtitle=Category:VGI_Domain&format=json&continue="
    # Exemple d'url pour récupérer la page par l'id
    # http://vgibox.eu/repository/index.php?curid=919

    # load file configuration
    config_file = 'config.yml'
    extract_abstracts(config_file)

    """
    <keywords> <key></key> </keywords>
    <title></title>
    <sentences></sentences>
    """
