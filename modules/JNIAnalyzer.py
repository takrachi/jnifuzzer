import re

# Reference : https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html#jvms-4.3
# TODO Considere pas les types avec des [ (arrays?) 
JAVA_TYPE = {
        "B" : "byte",
        "C" : "char",
        "D" : "double",
        "F" : "float",
        "I" : "int",
        "J" : "long",
        "S" : "short",
        "Z" : "boolean",
        "V" : "void",
    }

class JNIAnalyzer:
    def __init__(self, so_file, class_data):
        self.so_file = so_file
        self.native_func = []
        self.functions = dict()

        self.read_so()
        self.read_class(class_data)

    def get_pkg(self):
        return '.'.join(i for i in self.native_func[0].split('_')[1:-2]) 

    def get_class(self):
        return self.native_func[0].split('_')[-2]

    def read_so(self):
        with open(self.so_file, 'rb') as f:
            for string in re.findall(b"([a-zA-Z_$]{4,})", f.read()):
                if b'Java_' in string and string.decode() not in self.native_func: 
                    self.native_func.append(string.decode())

    def read_class(self, data):
        # find parameters of functions
        for func in self.native_func:
            func_name = func.split("_")[-1] 
            index = data.find(str.encode(func_name))
            
            # if native funcion called in class file
            if index != -1:
                index = index + len(func_name) + 2
                l_params = int(data[index])
                params = data[index + 1:index + l_params + 1].decode()
                
                self.functions[func_name] = dict()
                
                # Functions arguments
                self.functions[func_name]["args"] = []

                args = re.findall("\((.*)\)", params)[0]
                arg_ref = re.findall("L(.*?);", args)
                arg_noref = re.sub("L(.*?);", "L", args)

                for i in range(len(arg_noref)):
                    if arg_noref[i] == "L": # reference a une classe
                        ref = arg_ref[0].split("/")[-1]
                        self.functions[func_name]["args"].append(ref)
                        arg_ref.pop(0)
                    else:
                        self.functions[func_name]["args"].append(JAVA_TYPE[arg_noref[i]])

                # Functions return value
                return_val = re.sub("\((.*)\)", "", params)

                if "L" in return_val[0]:
                    ref = re.findall("L(.*?);", return_val)[0]
                    return_val = ref.split("/")[-1]
                #elif "[" in return_val[0]:
                    
                else:
                    return_val = JAVA_TYPE[return_val]

                self.functions[func_name]["return"] = return_val

