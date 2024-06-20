# Knowledge Pack Integration

## Library Format
Follow the steps below to integrate a library object into an ESP32 project.

1. Add the contents of the firmware folder from the downloaded `.zip` file into the folder
   structure of the target ESP32 project.

2. Open the target project within ESP32 IDE.

3. In the resulting window that opens, select the archive file (`sensiml/lib/libsensiml.a`), 
   and add it to the project.

4. Add the path to the `inc` folder (e.g., `sensiml/inc`) into your ESP32 compiler include path.

5. The folder 'application/' may have a source file (i.e., a .c file) which can be added to the 
   proejct.

6. The 'model.json' must be added to the project.

## Arduino Format
Follow the steps below to directly integrate the library into an ESP32 project.

1. Add the contents of the downloaded `.zip` file usng 'Sketch/Include Library/Add .ZIP Libary'
   option in to the Arduino project.

2. The library ('libsensiml.a') is the folder 'src/esp32' folder.

3. There is an example arduino code in the folder 'src/examples/sml_runner' which can be used 
   to check the library.

4. For using the Knowledge Pack,  add kb_model_init() to your init() function.
   Then Pass sensor data to the sml_run_model API in your loop() function.

6. If there is a function used that is not listed in 'keywords.txt', that can be added using 
   the .h files from the folder 'src/' in the .zip file.

## Source Format
Follow the steps below to directly integrate the source code into an ESP32 project.

1. Add the contents of the firmware folder from the downloaded `.zip` file into the folder
   structure of the target ESP32 project.

2. Open the target project within ESP32 IDE.

3. In the resulting window that opens, select the source folder (`sensiml/src/`), and add 
   it to the project.

4. Add the path to the `inc` folder (e.g., `sensiml/inc`) into your ESP32 compiler include path.

5. The folder 'application/' may have a source file (i.e., a .c file) which can be added to the 
   proejct.

6. The 'model.json' must be added to the project.

7. If source is not used then the library file (`sensiml/lib/libsensiml.a`) can be used.


