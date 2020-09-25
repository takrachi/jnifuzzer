# JNI Fuzzer

Recherche et développement d'une application qui permettrait de fuzzer la partie native d'un programme Java utilisant JNI (Java Native Interface).

### Description

Petite application en Python 3 qui permet d'analyser des fichiers .jar, .class et .so afin de sortir les fonctions JNI et créer une application Java à partir d'un gabarit pour faire appel à ces fonctions et finalement les fuzzer.

L'application prend en argument un fichier shared object (.so) puis un JAR ou bien un fichier java compilé (.class). Elle va déterminer quelle sont les fonctions natives appelées par le code Java, sortir les signatures et créer un code Java à partir du gabarit `template/Template.java` qui load la librairie compilée et appel les fonctions qu'on considère fuzzable (pour l'instant c'est seulement les arguments de type String). 

Le code Java sera compilé et roulé en passant comme input du data qui a été généré avec **Radamsa** qui se retrouve dans le fichier `data/fuzzing_data_string`. L'application pour l'instant vérifie si le programme Java roule toujours pour vérifier s'il y a eu un crash.

### Usage

| Argument         | Définition                                    | Exemple                                      |
| ---------------- | --------------------------------------------- | -------------------------------------------- |
| -s, --so=FILE    | Librarie compilée de type shared object (.so) | ./fuzzer.py -s libnative.so -c Example.class |
| -c, --class=FILE | Fichier Java compilé (.class)                 | ./fuzzer.py -s libnative.so -c Example.class |
| -j, --jar=FILE   | Fichier JAR                                   | ./fuzzer.py -s libnative.so -j app.jar       |



### Exemple d'utilisation

```bash
$ python fuzzer.py -s examples/AdminCheck/libnative.so -c examples/AdminCheck/BufferOverflow.class
[*] Reading shared object libnative.so and looking for JNI calls
[*] Reading class examples/AdminCheck/BufferOverflow.class and looking for JNI signatures
[*] Creating BufferOverflow.java from template
[+] Java program created in test/BufferOverflow.java
[*] Compiling with command: javac test/BufferOverflow.java
[*] Running with command: java -cp . -Djava.library.path=/home/rachel/jnifuzzer/examples/AdminCheck/libnative.so test.BufferOverflow

[+] Starting to fuzz
[-] Done

!! Crash detected: *** stack smashing detected ***: terminated

[!] Nothing to do, bye bye
```

Le programme reproduit la structure de la class BufferOverflow dans le dossier `test/` et fait appel à une fonction native du shared objet libnative.so puis fuzz celle-ci en lui donnant des paramètres qui ont été générés par Radamsa. Un crash a été détecté et donc le programme quitte. 

Code source de libnative.so

```c++
#include <iostream>
#include <cstring>
#include "test_BufferOverflow.h"

JNIEXPORT void JNICALL Java_test_BufferOverflow_checkAdmin (JNIEnv* env, jobject thisObject, jstring juser, jstring jpass) {
    int admin = 0;
    char username[10];
    char password[10];

    const char * user = env->GetStringUTFChars(juser, NULL);
    const char * pass = env->GetStringUTFChars(jpass, NULL);

    strcpy(username, user);
    strcpy(password, pass);

    if (std::strcmp(username, "admin") == 0 && std::strcmp(password, "secret") == 0) 
        admin = 1;
    
    if (admin) {
        std::cout << "Welcome Admin\n";
        std::cout << (char) admin;
    }
    else
        std::cout << "Not Admin\n";
}
```

### Radamsa

Test case generator : [GitLab](https://gitlab.com/akihe/radamsa)

Il est utilisé pour générer des fichiers avec du data à input au fuzzer.

```bash
echo "AAA" | radamsa -n 1000 > data/fuzzing_data_string
```



### Développement futur

Pour l'instant, le programme fuzz seulement sur des variables en argument de type String. Ce serait intéressant de faire pareil pour les entiers. Ce serait aussi intéressant d'être capable de créer un objet d'une classe de l'application et d'utiliser ses attributs pour agrandir la portée du fuzzer.

##### TODO

* Si un argument contient une classe custom, il faudrait qu'elle soit copiée (extraite du JAR) et placé avec le code Java utilisé pour fuzzer la librairie.
* Le programme ne gère pas les types array avec la signature [.
* Ce serait intéressant d'ajouter une fonctionnalité qui permet de trouver les liens entres un JAR et plusieurs fichier .so pour trouver c'est quelle classe qui fait appel à des fonctions natives automatiquement.
* Le programme généré à partir du gabarit teste toutes les fonctions natives en même temps avec le même argument. Ce serait intéressant de le séparer en plusieurs arguments.



## Références

#### Java Native Interface

* [Baeldung - Guide to JNI](https://www.baeldung.com/jni)
* [Oracle - JNI Functions](https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/functions.html)
* [Oracle - JNI Types and Data Structures](https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/types.html)

#### JNI Reversing

* [Android App Reverse Engineering 101](https://maddiestone.github.io/AndroidAppRE/reversing_native_libs.html)
* [Github - JNI Analyzer](https://github.com/maaaaz/jnianalyzer)

#### Fuzzing 

* [Github - jnizz - JNI Fuzzing Tool for Android](https://github.com/jeon95u/jnizz)
* [OWASP - Fuzzing](https://owasp.org/www-community/Fuzzing)
* [OWASP - Fuzz Vectors](https://owasp.org/www-project-web-security-testing-guide/latest/6-Appendix/C-Fuzz_Vectors)
* [GitLab - Radamsa - Test case generator](https://gitlab.com/akihe/radamsa)

#### Java class file structure

* [Wikipedia - Java class file](https://en.wikipedia.org/wiki/Java_class_file)
* [Oracle - JVM specs - Class File Format](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html#jvms-4.3)
* [Hacking Java Bytecode for Programmers](https://www.jaredfolkins.com/hacking-java-bytecode-for-programmers-part1-the-birds-and-the-bees-of-hex-editing/)



