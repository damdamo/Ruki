#! /usr/bin/env python3

import requests

URL_SERVER = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien/statements'

def import_rdf_to_rdf4j(rdf_file, method_name):
    """Take an rdf_file and import data in the server rdf4j"""

    # We load the file and put it in a string format
    # We separate prefix and n triples
    # We modify the format of prefix to have the good format for request
    # Example: We change @prefix by PREFIX and be clear the end dot '.'

    n3_triples = ''
    prefixes = ''

    with open(rdf_file, 'r') as rdf_file:
        for line in rdf_file:
            # If it's a prefix
            if 'prefix' in line:
                prefix_clean = line.replace('@prefix', 'PREFIX')

                # We don't take the last dot at the end
                prefix_split = prefix_clean.split()
                prefix_split.pop(len(prefix_split)-1)
                prefix_clean = ' '.join(prefix_split)
                prefixes = '{}\n{}'.format(prefixes, prefix_clean)
            else:
                n3_triples = '{}\n{}'.format(n3_triples, line)

    uri_name = '{}/{}'.format('http://cui.unige.ch', method_name)

    # Now we prepare the request
    # insertQuery is what we give with informations to add
    insertQuery = '''%s
                    INSERT DATA{
                    GRAPH <%s>{
                        %s
                    }
                    }''' % (prefixes, uri_name, n3_triples)

    #print(insertQuery)

    # Request with data and headers
    data = {'update': insertQuery}
    headers = {'Accept':'application/sparql-results+json, */*;q=0.5', 'Accept-Charset': 'UTF-8', 'Content-Type': 'application/x-www-form-urlencoded'}
    result = requests.post(URL_SERVER, data=data, headers=headers)

    print(result)
    print(result.headers)
    my_text = (result.content).decode("utf-8")
    print(my_text.split('\r\n'))

if __name__ == '__main__':

    import_rdf_to_rdf4j('temp/yml_example_to_add_method.rdf')
