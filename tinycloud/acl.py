import config
import os
import yaml

class acl:
    def __init__(self,confdir):
        aclfile = open(os.path.join(confdir, "acl.yaml"))
        self.acl = yaml.safe_load(aclfile.read())
        print(self.acl)

    def check(self, path, user):
        if not user in self.acl:
            return True
        for i in self.acl[user]["deny"]:
            if path.startswith(i):
                return False
            return True
