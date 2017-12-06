#! /usr/bin/env python3

import yaml

def load_config(config_file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config

def write_rdf(file_name, rdf_to_write):
    """ Take a string and write it into a file """
    # If we have multiple file we write on it
    with open(file_name, 'w') as output_file:
        output_file.write("{}".format(rdf_to_write))
