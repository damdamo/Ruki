#! /usr/bin/env python3

import requests

if __name__ == '__main__':

    url = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien'

    query1 = 'ask {?s ?p ?o}'
    query2 = 'construct {?s ?p ?o} where {?s ?p ?o}'
    query4 = '''# List all articles
    PREFIX cui: <http://cui.unige.ch/>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX vgiid: <http://vgibox.eu/repository/index.php?curid=>
    PREFIX xml: <http://www.w3.org/XML/1998/namespace>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

      # List all articles
        SELECT DISTINCT ?a
        WHERE {
          ?a a cui:article .
        }'''

    payload = {'query': '{}'.format(query4), 'queryLn':'SPARQL'}



    result = requests.get(url, params=payload)

    # url = 'http://kr.unige.ch:8080/rdf4j-server/repositories/master_project_damien?query=ask {?s ?p ?o}'

    # result = requests.get(url)

    print(result)
    print(result.url)
    print(result.content)
