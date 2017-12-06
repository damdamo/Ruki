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


def get_concept_name(ontology):
    """ Take an ontology
    Return a list with all concept name of this ontology
    ontology is created by the function load ontology """

    # We create a list to put our concepts
    list_concept = []

    for concept in ontology.classes():

        # Return a string with the concept name normalized
        concept_name_clean = clean_concept(concept)
        # We add our concept into the list
        list_concept.append(concept_name_clean)

    return list_concept


def clean_concept(concept):
    """clean_concept can clean and normalized concept of the list_concept
    In this function we:
    - Replace underscore by a space
    - Replace all uppercase by lowercase """

    concept_name = concept.name
    concept_name_normalized = concept_name.replace('_', ' ')
    concept_name_normalized = concept_name_normalized.lower()

    # This part has goal to suppress the repitition inside the concept
    # name, but some element are not unique after this operation
    """concept_name_normalized = concept_name_normalized.split()
    class_parent = str(concept.is_a)
    for word in concept_name_normalized:
        if word in class_parent:
            concept_name_normalized.remove(word)

    concept_name_normalized = ' '.join(concept_name_normalized)"""

    return concept_name_normalized


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

    # TODO: Regarder le nom des concepts pour enlever la répétition

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
                    dic_concept_abstract[ontology][abstract_id][concept] = abstract_clean.count(
                        concept)

    return dic_concept_abstract

    # print(dic_concept_abstract['onto1_correct'])

def rdf_translate(dic_concept_abstract, file_name):
    """rdf translate take the dic_concept_abstract and translate it
    into rdf format with rdflib
    For the merge with main file, we just need to have the same URI for each
    document"""

    rdf_graph = Graph()

    vgiid = Namespace('http://vgibox.eu/repository/index.php?curid=')
    cui = Namespace('http://cui.unige.ch/')

    rdf_graph.bind("vgiid", vgiid)
    rdf_graph.bind("cui", cui)
    rdf_graph.bind("skos", SKOS)
    rdf_graph.bind("rdfs", RDFS)

    # Construction of rdf
    for ontology in dic_concept_abstract:
        rdf_graph.add((cui[ontology], RDF.type, cui.knowledge_extractor_result))
        rdf_graph.add((cui[ontology], RDFS.subClassOf, SKOS.ConceptScheme))
        rdf_graph.add((cui[ontology], SKOS.prefLabel, Literal(ontology)))
        for abstract_id in dic_concept_abstract[ontology]:
            rdf_graph.add((vgiid[abstract_id], RDF.type, cui.article))
            for concept in dic_concept_abstract[ontology][abstract_id]:
                concept_with_underscore = concept.replace(' ', '_')
                rdf_graph.add((cui[concept_with_underscore], RDFS.subClassOf, SKOS.Concept))
                rdf_graph.add((cui[concept_with_underscore], SKOS.inSchema, cui[ontology]))
                rdf_graph.add((cui[concept_with_underscore], SKOS.prefLabel, Literal(concept)))
                if dic_concept_abstract[ontology][abstract_id][concept] > 0:
                    number = dic_concept_abstract[ontology][abstract_id][concept]
                    index_name = 'index_{}_{}'.format(abstract_id, concept_with_underscore)
                    rdf_graph.add((cui[index_name], RDF.type, cui.art_concept_link))
                    rdf_graph.add((cui[index_name], cui.has_concept_name, Literal(concept)))
                    rdf_graph.add((cui[index_name], cui.has_article, vgiid[abstract_id]))
                    rdf_graph.add((cui[index_name], cui.has_number, Literal(number)))

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
        list_concept = get_concept_name(ontology)
        # write_concepts('concepts.txt', list_concept)
        concept_dic[ontology.name] = list_concept

    dic_concept_abstract = find_concept_abstract(concept_dic, abstract_folder)

    if config['rdf']['write_rdf']:
        rdf_translate(dic_concept_abstract, config['rdf']['file_name'])

    return dic_concept_abstract

if __name__ == '__main__':

    # load file configuration
    config_file = 'config/config_ontologies.yml'
    extract_onto_concepts(config_file)
