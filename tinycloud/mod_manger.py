import importlib
import sys

class _mod_manger():
    def load_mod(self,name):
        setattr(self,name,__import__(name,fromlist=name.split(".")[-1]))
mod_manger=_mod_manger()
