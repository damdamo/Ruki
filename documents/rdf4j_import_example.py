#! /usr/bin/env python3

import requests

if __name__ == '__main__':

    url = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien/statements'

    path_rdf = '../Results/Rdf/save_rdf4j0.n3'
    #path_rdf = '../Results/Rdf/rdf_onto_extraction.rdf'

    n3_triples = ''
    prefixes = ''

    with open(path_rdf, 'r') as n3_file:
        for line in n3_file:
            if 'prefix' in line:
                lol = line.replace('@prefix', 'PREFIX')
                lol = lol.replace('.','')
                prefixes = '{}{}'.format(prefixes, lol)
            else:
                n3_triples = '{}\n{}'.format(n3_triples, line)

    insertQuery = '''%s
                    INSERT DATA{
                    GRAPH <http://cui.unige.ch/test>{
                        %s
                    }
                    }''' % (prefixes, n3_triples)

    print(insertQuery)

    files = {'data':'{}'.format(open(path_rdf, 'rb'))}
    data = {'update': insertQuery}

    headers = {'Accept':'application/sparql-results+json, */*;q=0.5', 'Accept-Charset': 'UTF-8', 'Content-Type': 'application/x-www-form-urlencoded'}
    result = requests.post(url, data=data, headers=headers)


    print(result)
    print(result.encoding)
    print(result.headers)
    #print(result.url)
    my_text = (result.content).decode("utf-8")
    print(my_text.split('\r\n'))
