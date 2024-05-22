import json
import configparser
import os


def read_json_file(path):
    new_dict = None
    with open(path, "r") as f:
        new_dict = json.load(f)
    return new_dict


def write_json_file(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


def read_conf_m():
    conf = configparser.ConfigParser()
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf.read(root_path + '/Mutation/config.conf', 'utf8')
    m = conf.get('model_name', 'm')
    return m
