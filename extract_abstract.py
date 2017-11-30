#! /usr/bin/env python3

import requests
import re
import string
import generic_functions as gf


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


def add_tag_into_file(file_name, tag):
    """A simple function to add a tag in a file
    file_name is the output file
    tag is a simple string"""
    with open(file_name, 'a') as output_file:
        output = '{}'.format(tag)
        output_file.write("{}".format(output))


def write_content_into_file(file_name, content, doc_id, options):
    """ Take a content and write it into a file
    file_name is the output file
    content is a dictionnary which contains all informations
    printable like abstract, title, keywords and id"""

    # If we have multiple file we write (erase the precedent content)
    # If we have all in one file we append the content
    if options['multiple_file']:
        choice = 'w'
    else:
        choice = 'a'

    abstract = ''

    if options['xml']:
        if options['id']:
            abstract = '<id>{}</id>\n'.format(doc_id)
        if options['title']:
            abstract = '{}<title>{}</title>\n'.format(
                abstract, content['title'])
        if options['keywords']:
            for keyword in content['keywords']:
                abstract = '{}<keyword>{}</keyword>'.format(abstract, keyword)
            abstract = '{}\n'.format(abstract)

        abstract = '{}<abstract>\n{}\n</abstract>'.format(
            abstract, content['abstract'])

        with open(file_name, choice) as output_file:
            if abstract != '':
                output = '<article>\n{}\n</article>\n'.format(abstract)
                output_file.write("{}".format(output))
    else:
        if options['id']:
            abstract = '{}\n'.format(doc_id)
        if options['title']:
            abstract = '{}{}\n'.format(abstract, content['title'])
        if options['keywords']:
            keywords = ', '.join(content['keywords'])
            abstract = '{}{}\n'.format(abstract, keywords)

        abstract = '{}{}\n'.format(abstract, content['abstract'])

        with open(file_name, choice) as output_file:
            if abstract != '':
                output = '{}\n'.format(abstract)
                output_file.write("{}".format(output))


def get_page_id(dic):
    """ Find id of a page and return it in a string type """
    list_article = dic['categorymembers']
    for element in list_article:
        yield str(element['pageid'])


def get_all_page_id(url, parameters_id):
    """ Get all page id from all articles
    url contains a simple url where we can find all articles
    parameters_id specify what we want for query (see config file)
    output is a dic with all informations of a page"""
    list_id = []
    # We obtain all id page
    for element in query(url, parameters_id):
        yield get_page_id(element)


def clean_abstract(abstract):
    """ Allow to remove useless component in the abstract
    like link. Regex can clean link and square roots
    We replace '&' by 'and' because it's not valide for xml
    Output is just string that contain clean abstract"""
    regex_link = re.compile(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    # regex_square_bracket = re.compile('[\[\]]')
    clean_abstract = re.sub(regex_link, '', abstract)
    # clean_abstract = re.sub(regex_square_bracket, '', clean_abstract)
    # clean_abstract = clean_abstract.replace('&', 'and')
    list_char_to_clean = '&[]'
    clean_abstract = clean_abstract.translate(str.maketrans(
        list_char_to_clean, ' ' * (len(list_char_to_clean))))

    return clean_abstract


def get_keywords(content):
    """ Collect all keywords from content with parsing
    Content is just the content of a web page wiki and we use a
    regex to keep only keywords.
    Output is a table with all keywords"""
    regex_get_keywords = re.compile('Keywords=(.)*\n')
    keywords = regex_get_keywords.search(content)

    # We verify that keywords exist
    if keywords is not None:
        keywords = keywords.group(0)
        # We keep only keywords
        keywords = keywords.replace('Keywords=', '')
        # We suppress line break and &
        keywords = keywords.replace('\n', '')
        list_char_to_clean = '&'
        keywords = keywords.translate(str.maketrans(
            list_char_to_clean, ' ' * (len(list_char_to_clean))))
        # For split we use a coma + a space
        table_keywords = keywords.split(', ')
        # We suppress the coma of the last word because we have a format like:
        # Keywords= k1, k2, k3, (with a comma at the end)
        table_keywords[len(
            table_keywords) - 1] = table_keywords[len(table_keywords) - 1].replace(',', '')

        return table_keywords

    # If there are any keywords, we return an empty table
    return []


def get_abstract_from_content(content):
    """ Get abstract from a content of a specific page """
    # We clear all line break (need for regex)
    content_mod = content.replace('\n', ' ')

    # Option to keep keywords

    table_keywords = get_keywords(content)
    regex_get_abstract = re.compile('{(.)*}( )?')
    abstract = re.sub(regex_get_abstract, '', content_mod)

    dic_content = {}
    dic_content['abstract'] = clean_abstract(abstract)
    # dic_content['keywords'] = keywords
    dic_content['keywords'] = table_keywords

    return dic_content


def get_all_abstract(url, list_all_id, parameters_extract_content):
    """ Collect all abstract
    url: url of the web page
    list_all_id: a list with id of all article
    parameters_extract_content: parameters for the query, avaible in file config
    return the content of all of the web page """
    dic_content = {}
    for gen_id in list_all_id:
        for my_id in gen_id:
            parameters_extract_content['pageids'] = my_id
            for element in query(url, parameters_extract_content):
                content = element['pages'][my_id]['revisions'][0]['*']
                dic_content[my_id] = get_abstract_from_content(content)
                dic_content[my_id]['title'] = element['pages'][my_id]['title']
                yield my_id, dic_content


def extract_abstracts(config_file):
    """ Extract all abstract of all Publication in the website
    and can put it in a single file or multiple files. It depends
    options in the file config """

    config = gf.load_config(config_file)

    # We extract id from articles
    parameters_id = config['parameters_id']
    url = config['url']

    # We collect all id
    list_all_id = get_all_page_id(url, parameters_id)
    parameters_extract_content = config['parameters_extract_content']

    i = 0

    # Initialization paramters for writing
    if config['options']['writing']:
        if config['options']['xml']:
            file_extension = '.xml'
        else:
            file_extension = '.txt'
        if not config['options']['multiple_file']:
            name_file = '{}{}'.format(config['output']['file'], file_extension)
            # If we have one file in xml format, we need to have a unique tag at the beginning
            # and the end of the document. We put the first tag
            if config['options']['xml']:
                add_tag_into_file(name_file, '<informations>\n')

    for doc_id, dic_content in get_all_abstract(url, list_all_id, parameters_extract_content):
        print('Abstract number: {}'.format(i))
        i = i + 1

        if config['options']['writing']:
            if config['options']['multiple_file']:
                name_file = '{}{}{}'.format(
                    config['output']['folder'], doc_id, file_extension)
                write_content_into_file(
                    name_file, dic_content[doc_id], doc_id, config['options'])

            else:
                write_content_into_file(
                    name_file, dic_content[doc_id], doc_id, config['options'])

        yield doc_id, dic_content

    if config['options']['writing']:
        # We put the last tag if we have a unique file for writing
        if not config['options']['multiple_file']:
            add_tag_into_file(name_file, '\n</informations>')


if __name__ == '__main__':

    # url_to_extract = "http://vgibox.eu/repository/api.php?action=query&list=categorymembers&cmtitle=Category:VGI_Domain&format=json&continue="
    # Exemple d'url pour récupérer la page par l'id
    # http://vgibox.eu/repository/index.php?curid=919

    # load file configuration
    config_file = 'config/config_extract.yml'

    for doc_id, dic_content in extract_abstracts(config_file):
        print('Document extraction id: {}'.format(doc_id))
