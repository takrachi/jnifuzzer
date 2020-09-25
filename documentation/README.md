# Java Native Interface 

Cette section contient quelques informations qui peuvent sauver du temps. Sinon dans la section Référence il y a plusieurs liens utiles qui permettent d'en apprendre plus sur JNI.

#### Termes intéressants à rechercher 

##### Chargement des librairies natives

```java
System.load("lib/libcalc.so");
System.loadLibrary("calc");
```

Les deux fonctions effectuent la même chose, la différence est que la deuxième charge la librairie à partir de son short name.

##### Déclaration d'une méthode native dans Java

``` java
package nompackage;

public class UneClasse {
    ...
    public native String uneFonctionNative(String arg1, int arg2);    
}
```

##### Décalaration d'une méthode native en C/C++

```c++
JNIEXPORT jstring JNICALL Java_nompackage_UneClasse_uneFonctionNative(JNIEnv* env, jobject thisObject, jstring arg1, jint arg2);
```

##### Signature des méthodes

Entre parenthèses, on retrouve les arguments de la méthode puis à l'extérieur la valeur de retour. Dans la méthode déclarée plus haut, la signature serait la suivante.

```
(Ljava/lang/String;I)Ljava/lang/String;
```

C'est avec ces signatures que le fuzzer détermine les arguments à envoyer lors du fuzzing.

Voir références pour la liste des types de signatures.

### Création d'un programme JNI

```bash
javac -h . test/HelloWorldJNI.java
```

```bash
export JAVA_HOME=/usr/lib/jvm/default
```

```bash
g++ -c -fPIC -I${JAVA_HOME}/include -I${JAVA_HOME}/include/linux test_HelloWorldJNI.cpp -o test_HelloWorldJNI.o
```

```bash
g++ -shared -fPIC -o libnative.so test_HelloWorldJNI.o -lc
```

```bash
java -cp . -Djava.library.path=/<native_lib_full_path> test.HelloWorldJNI
```
