import exceptions


class mod_manger:
    def __init__(self, tinycloud):
        self.tinycloud = tinycloud
        self.mods = {}

    def load_mod(self, name):
        mod = __import__(name, fromlist=name.split(".")[-1])
        if not hasattr(mod, "PROVIDE"):
            raise exceptions.ModuleInvalidError("Not a valid module")
        mod.TINYCLOUD = self.tinycloud
        self.mods[name] = mod

    def require_mod(self, modname, modtype):
        if not modname in self.mods:
            raise ModuleNotFoundError("Module {} not found")
        mod = self.mods[modname]

        if not modtype in mod.PROVIDE:
            raise ModuleNotFoundError(
                "{} dosn't provide {}".format(modname.title(), modtype)
            )
        return mod.PROVIDE[modtype]
    def load_require(self,modname,modtype):
        self.load_mod(modname)
        return self.require_mod(modname,modtype)
