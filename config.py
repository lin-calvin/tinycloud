import yaml

def load_conf(path):
    global conf
    file=open(conf_path)
    conf=yaml.safe_load(file.read())
