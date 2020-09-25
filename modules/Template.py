from os import path, mkdir

# TODO 
# Seulement le String est fuzze
# Voir si les valeurs par defauts devraient etre changees ou considerees
# Pour l'instant c'est la meme variable qui est utilisee pour fuzzer plusieurs types
PARAMS_DEFAULT = {
        "byte"   : "1",
        "char"   : "'A'",
        "double" : "1", 
        "float"  : "1",
        "int"    : "1", 
        "long"   : "1",
        "String" : "fuzz_vector",
        "short"  : "1",
        "boolean": "true"
    }

class Template:
    NATIVE_METH_STR = "private native %s %s(%s);"
    NATIVE_CALL_STR = "new %s().%s(%s);"
    PKG_STR = "package %s;"
    TEMPLATE_DIR = "template/Template.java"

    def __init__(self, jni):
        self.so_path = path.abspath(jni.so_file)
        self.pkg = jni.get_pkg()
        self.class_name = jni.get_class()
        self.methods = []
        self.calls = []

        self.set_methodscalls(jni.functions)

    def set_methodscalls(self, functions):
        for name in functions:
            return_value = functions[name]["return"]
            params = functions[name]["args"]

            # Skip les fonctions non fuzzees
            if "String" in params:
                method_params = ', '.join([params[i] + " p%i" % (i+1) for i in range(len(params))])
                call_params = ', '.join([PARAMS_DEFAULT[p] for p in params])

                self.methods.append(self.NATIVE_METH_STR % (return_value, name, method_params))
                self.calls.append(self.NATIVE_CALL_STR % (self.class_name, name, call_params))

    def get_pkg(self):
        if self.pkg:
            return self.PKG_STR % self.pkg
        else:
            return ""

    def get_methods(self):
        return '\n    '.join(self.methods)

    def get_calls(self):
        return '\n            '.join(self.calls)

    def generate_template(self):
        template = open(self.TEMPLATE_DIR, 'r').read()

        template = template.replace("<so_path>", self.so_path)
        template = template.replace("<package_name>", self.get_pkg())
        template = template.replace("<class_name>", self.class_name)
        template = template.replace("<native_methods>", self.get_methods())
        template = template.replace("<native_calls>", self.get_calls())

        #print (template)

        if not path.exists(self.pkg):
            mkdir(self.pkg)
            app_path = self.pkg + "/" + self.class_name + ".java"
            open(app_path, 'w').write(template)
            print ("[+] Java program created in " + app_path)

        else:
            print ("[x] Unable to create directory " + self.pkg)
