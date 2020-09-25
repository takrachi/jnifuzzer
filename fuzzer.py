#!/usr/bin/env python3

from modules.JNIAnalyzer import JNIAnalyzer
from modules.Template import Template
from modules.JNIFuzzer import JNIFuzzer
import zipfile
from optparse import OptionParser
import re
from os import listdir

def isLinked(so_name, class_data):
    short_so_name = str.encode(re.sub("lib|.so.*", "", so_name)) # libABC.so -> ABC
    so_name = str.encode(so_name)

    if so_name in class_data:
        return True
    elif b'loadLibrary' in class_data and short_so_name in class_data:
        return True
    
    return False

def main(options, args):
    if options.link_dir:
        folder = options.link_dir
        folder = ((folder + "/") if "/" not in folder[-1] else folder)
        files = listdir(folder)

        so_files = [folder + i for i in files if '.so' in i]
        jar_files = [folder + i for i in files if '.jar' in i]

        for jar in jar_files:
            jar_data = zipfile.ZipFile(jar)

            for jfile in jar_data.namelist():
                if '.class' in jfile:
                    for so in so_files:
                        if isLinked(so.split("/")[-1], jar_data.read(jfile)):
                            print ("CLASS: " + jfile + " in " + jar + " is linked with " + so)

    elif options.so_file:
        so_name = options.so_file.split("/")[-1] #libABC.so
        class_data = None
        class_file = options.class_file
        
        print ("[*] Reading shared object " + so_name + " and looking for JNI calls")

        # JAR FILE
        if options.jar_file:
            jar = zipfile.ZipFile(options.jar_file)
            
            for jfile in jar.namelist():
                if '.class' in jfile:
                    data = jar.read(jfile)

                    if isLinked(so_name, data):
                        class_data = data
                        class_file = jfile
        
        # CLASS FILE
        elif class_file:
            data = open(class_file, 'rb').read()
            if isLinked(so_name, data):
                class_data = data

        else:
            print ("Please specify a jar file or a class file")
            exit(0)

        # S'il n'y a pas de lien entre la librairie et la classe, on quitte
        if not class_data:
            print ("[x] No link between " + so_name + " and the class/jar files specified. Nothing to do.")
            exit(0)
        
        
        print ("[*] Reading class " + class_file + " and looking for JNI signatures")

        # Analyse des fichiers class et so pour sortir les fonctions JNI   
        jni = JNIAnalyzer(options.so_file, class_data)

        # If there's JNI calls in the class file then fuzz it
        if jni.functions:
            # Creation d'un programme java pour call les fonctions JNI
            app = Template(jni)
            print ("[*] Creating " + app.class_name + ".java from template")
            app.generate_template()
            
            # Fuzzing des fonctions 
            fuzzer = JNIFuzzer(app.so_path, app.class_name, app.pkg)
            fuzzer.fuzz()
        else:
            print ("[x] Looks like there's a link between " + class_file + " and " + so_name + " but no native calls found in the Java code")

    else:
        print ("Please specify a .so file with -s option")
        exit(0)




if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-s", "--so", 
            dest="so_file",  
            help="shared object file with JNI calls", 
            metavar="SO_FILE")

    parser.add_option("-j", "--jar", 
            dest="jar_file", 
            help="jar file (optional if class file specified)", 
            metavar="JAR_FILE")

    parser.add_option("-c", "--class", 
            dest="class_file", 
            help="class file (optional if jar file specified)", 
            metavar="CLASS_FILE")

    parser.add_option("-l", "--link", 
            dest="link_dir", 
            help="Find in which class the shared object is imported",
            metavar="DIR")

    (options, args) = parser.parse_args()
    
    main(options, args)
