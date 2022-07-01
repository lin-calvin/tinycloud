import yaml

def load_conf(path):
    global conf
    file=open(path)
    conf=yaml.safe_load(file.read())
