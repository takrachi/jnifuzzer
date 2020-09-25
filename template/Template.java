<package_name>

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class <class_name> { 

    static { 
        System.load("<so_path>");
    }

    public static void main(String[] args) throws IOException {
        BufferedReader r = new BufferedReader(new InputStreamReader(System.in));

        while (true) {
            String fuzz_vector = r.readLine();
            <native_calls>
        }
    }

    <native_methods>
}
