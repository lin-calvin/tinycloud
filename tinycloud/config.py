import yaml
import os


def load_conf(path):
    global conf
    global conf_dir
    conf_dir = os.path.dirname(path)
    file = open(path)
    conf = yaml.safe_load(file.read())
