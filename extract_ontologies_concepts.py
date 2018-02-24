#! /usr/bin/env python3

from owlready2 import *
from nltk.corpus import stopwords
import string
import re
import generic_functions as gf

from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, RDFS


def write_concepts(file_name, concepts):
    """ Take a string and write it into a file """
    # If we have multiple file we write on it
    with open(file_name, 'w') as output_file:
        for concept in concepts:
            output = '{}\n'.format(concept)
            output_file.write("{}".format(output))


def load_ontology(ontology_path, ontology_name):  # ontology_name
    """ Take the ontology path and ontology name and return the ontolgy
    CARE the ontolgy path must be ABSOLUTE ! """
    # list_ontologies = os.listdir(ontology_path)
    onto_path.append(ontology_path)
    ontology = get_ontology(ontology_name).load()
    return ontology


def get_concept_uri(ontology):
    """ Take an ontology
    Return a list with all concept name of this ontology
    ontology is created by the function load ontology """

    # We create a list to put our concepts
    list_concept = []

    for concept in ontology.classes():
        list_concept.append(concept)

    return list_concept


def get_concept_name(concept_uri):
    """get_concept_name take the concept_uri and extract the name"""


    if len(concept_uri.label) == 0:
        concept_name = concept_uri.name
        concept_name = concept_name.replace('_', ' ')
        concept_name = concept_name.lower()
    else:
        concept_name = concept_uri.label[0]

    return concept_name


def clean_abstract(abstract):
    """clean_abstract can clean and normalized abstract
    In this function we:
    - Replace all uppercase by lowercase
    - Delete stopwords

    We return a table of string"""
    abstract_clean = abstract.lower()
    # We clean all stopwords with list of nltk
    abstract_clean = ' '.join([word for word in abstract_clean.split(
    ) if word not in stopwords.words('english')])

    # The fast way to clean all the punctuation
    abstract_clean = abstract_clean.translate(str.maketrans(
        string.punctuation, ' ' * (len(string.punctuation))))
    abstract_clean = abstract_clean.split()

    return abstract_clean


def find_concept_abstract(concept_dic, abstract_folder):
    """Take the dictionnary with concept and a folder with
    all abstracts.
    Return a new dictionnary where we count for each ontology
    the number of time where a concept appear
    Format: dic = {'onto1':{'abstract1':{'concept1': nb_occurence},...},...}
    """

    dic_concept_abstract = {}
    list_abstract_file = os.listdir(abstract_folder)
    # Regex rule to clean extension
    clean_extension = re.compile('[.](.)*')

    for ontology in concept_dic:
        dic_concept_abstract[ontology] = {}
        for abstract_file in list_abstract_file:
            # We clean the extension to add id number as key
            abstract_id = re.sub(clean_extension, '', abstract_file)
            dic_concept_abstract[ontology][abstract_id] = {}
            file_name = '{}{}'.format(abstract_folder, abstract_file)
            with open(file_name, 'r') as output_file:
                abstract = output_file.read()
                abstract_clean = clean_abstract(abstract)
                for concept in concept_dic[ontology]:
                    concept_clean = get_concept_name(concept)
                    dic_concept_abstract[ontology][abstract_id][concept] = abstract_clean.count(
                        concept_clean)

    # print(dic_concept_abstract['onto1_correct'])

    return dic_concept_abstract

def rdf_translate(dic_concept_abstract, file_name):
    """rdf translate take the dic_concept_abstract and translate it
    into rdf format with rdflib
    For the merge with main file, we just need to have the same URI for each
    document"""

    rdf_graph = gf.basic_knowledge_graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    schema = Namespace('http://schema.org/')
    cui = Namespace('http://cui.unige.ch/')

    """rdf_graph.bind("vgiid", vgiid)

    rdf_graph.bind("skos", SKOS)
    rdf_graph.bind("rdfs", RDFS)"""

    # Construction of rdf
    for ontology in dic_concept_abstract:
        rdf_graph.add((cui[ontology], RDF.type, cui.knowledge_extractor_result))
        rdf_graph.add((cui[ontology], RDFS.subClassOf, SKOS.ConceptScheme))
        rdf_graph.add((cui[ontology], SKOS.prefLabel, Literal(ontology)))
        for abstract_id in dic_concept_abstract[ontology]:
            rdf_graph.add((vgiid[abstract_id], RDF.type, schema.Article))
            for concept_uri in dic_concept_abstract[ontology][abstract_id]:
                concept_uri_term = URIRef(concept_uri.iri)
                super_concept_uri = (concept_uri.is_a)[0].iri
                super_concept_uri_term = URIRef(super_concept_uri)
                rdf_graph.add((concept_uri_term, RDFS.subClassOf, super_concept_uri_term))
                rdf_graph.add((concept_uri_term, RDFS.subClassOf, SKOS.Concept))
                rdf_graph.add((concept_uri_term, SKOS.inSchema, cui[ontology]))
                rdf_graph.add((concept_uri_term, SKOS.prefLabel, Literal(get_concept_name(concept_uri))))
                if dic_concept_abstract[ontology][abstract_id][concept_uri] > 0:
                    number = dic_concept_abstract[ontology][abstract_id][concept_uri]
                    index_name = 'index_{}_{}'.format(abstract_id, concept_uri.name)
                    blank_node = BNode(index_name)
                    rdf_graph.add((blank_node, RDF.type, cui.art_concept_link))
                    rdf_graph.add((blank_node, cui.has_article, vgiid[abstract_id]))
                    rdf_graph.add((blank_node, cui.has_number, Literal(number)))
                    if len(concept_uri.label) == 0:
                        rdf_graph.add((blank_node, cui.has_concept, cui[concept_uri.name]))
                    else:
                        rdf_graph.add((blank_node, cui.has_concept, cui[concept_uri.label[0]]))

    # We normalize in n3 to write it
    rdf_normalized = rdf_graph.serialize(format='n3')
    rdf_normalized = rdf_normalized.decode('utf-8')
    gf.write_rdf(file_name, rdf_normalized)


def extract_onto_concepts(config_file):
    """Main function
    Return the dictionnary that we obtain with
    find_concept_abstract. It can write this dictionnary
    in a rdf format"""

    config = gf.load_config(config_file)
    ontology_path = config['ontologies']['path']
    abstract_folder = config['abstract_folder']

    # We create a dic where for each ontology we create
    # a key which contains all concepts for this ontology
    concept_dic = {}

    for ontology_name in os.listdir(ontology_path):
        ontology = load_ontology(ontology_path, ontology_name)
        list_concept_uri = get_concept_uri(ontology)
        # list_concept_name = get_list_concept_name(list_concept_uri)

        # write_concepts('concepts.txt', list_concept)
        concept_dic[ontology.name] = list_concept_uri

    dic_concept_abstract = find_concept_abstract(concept_dic, abstract_folder)

    if config['rdf']['write_rdf']:
        rdf_translate(dic_concept_abstract, config['rdf']['file_name'])

    return dic_concept_abstract

if __name__ == '__main__':

    # load file configuration
    config_file = 'config/config_ontologies_concepts.yml'
    extract_onto_concepts(config_file)
