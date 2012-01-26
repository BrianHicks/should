'config parser for should'
from os import path, getcwd

import yaml

DEFAULT_CONFIG = {
    'path': path.expanduser('~/.should/'),
    'chars': {
        'project': '+',
        'tag': '@',
        'dependency': '^',
        'start date': ':',
        'end date': ';',
    }
}

def get_config(extra_paths=None, exclude_local=False):
    'combine config files'
    base_config_name = '.shouldrc.yaml'
    paths = (
        path.expanduser('~/%s' % base_config_name),
        path.join(getcwd(), base_config_name)
    )

    if extra_paths != None:
        paths += tuple(extra_paths)

    config = dict(DEFAULT_CONFIG)
    for config_path in paths:
        try:
            with open(config_path, 'rb') as config_file:
                config.update(yaml.load(config_file.read()))
        except IOError:
            pass

    return config

def merge_configs(orig, new):
    'merge two configuration dictionaries'
    for key, value in new.items():
        # merge if we can, set if key is not present
        if key in orig:
            if isinstance(value, list) and \
               isinstance(orig[key], list):
                orig[key] += value
                continue

            elif isinstance(value, dict) and \
                 isinstance(orig[key], dict):
                orig[key] = merge_configs(orig[key], value)
                continue

            # more special values here, if needed

        orig[key] = value

    return orig
