import subprocess
from time import sleep

class JNIFuzzer:
    def __init__(self, so_path, class_name, pkg_name):
        self.so_path = so_path
        self.class_name = class_name
        self.pkg = pkg_name

    def fuzz(self):
        # Compilation 
        args = ['javac', self.pkg + "/" + self.class_name + ".java"]
        
        print ("[*] Compiling with command: " + ' '.join(args))

        process = subprocess.Popen(args, 
                stdout = subprocess.PIPE, 
                universal_newlines = True)
        
        sleep(1) # Wait for compilation

        # Run
        args = ["java", 
                "-cp", 
                ".", 
                "-Djava.library.path=" + self.so_path, 
                self.pkg + "." + self.class_name]

        print ("[*] Running with command: " + ' '.join(args))

        app = subprocess.Popen(args, 
                stdin = subprocess.PIPE, 
                stdout = subprocess.PIPE, 
                stderr = subprocess.PIPE, 
                universal_newlines = True, 
                bufsize = 0)
         
        # Fuzzing
        print ("\n[+] Starting to fuzz")
        with open("data/fuzzing_data_string", "rb") as f:
            for data in f.read().splitlines():
                sleep(0.05)
                #print (data)
                try:
                    #TODO Peut-etre mieux d'utiliser communicate() return value communicate
                    #app.communicate(data.encode() + '\n')
                    app.stdin.write(data.decode('latin-1') + '\n')
                except BrokenPipeError:
                    break

        app.stdin.close()

        print ("[-] Done")

        for line in app.stderr:
            print("\n!! Crash detected: " + line.strip())
        

        print ("\n[!] Nothing to do, bye bye")
