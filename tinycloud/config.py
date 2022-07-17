import yaml
import os

class config:
    def load_conf(self,path):
        self.file_name =path
        file = open(path,"r")
        self.conf = yaml.safe_load(file.read())
        file.close()
    def save_conf(self):
        file=open(self.file_name,"w")
        yaml.dump(self.conf,file)
