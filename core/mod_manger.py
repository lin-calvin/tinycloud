import importlib
class mod_manger():
    def load_mod(self,name,path=""):
        if path!="":
            spec=importlib.util.spec_from_file_location(name,path+name+".py")
            mod=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            setattr(self,name,mod)
        else:
            setattr(self,name,__import__(name))
            print(dir(self))
        
