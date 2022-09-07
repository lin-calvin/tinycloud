import yaml


class acl:
    def __init__(self, conf):
        aclfile = open(conf)
        self.acl = yaml.safe_load(aclfile.read())

    def check(self, path, user):
        if not user in self.acl:
            return True
        for i in self.acl[user]["deny"]:
            if path.startswith(i):
                return False
            return True
