#! /usr/bin/env python3

import yaml

def load_config(config_file):
    """ Load the config file """
    with open(config_file, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    return config
