Jeeves
-------------
main function is located to **Jeeves** class at the moment mainly for testing reasons.

Compile & run Jeeves
-------------

`cd Jeeves`

`mvn package`

`mvn dependency:copy-dependencies`

`java -jar target/jeeves-1.0.jar`


Run manually JobDescriptor
-------------

If you need to run manualy one of the input-examples inside example/ folder:
* copy the example you need to jobdescriptor0.json file
* call the corresponding function for splitting files inside main functrion in class Jeeves

(WARNING) tests are only for the three basic functions (Split_Equal, Split_Proportional and Split_Next) which work with jobdescriptor0_init.json format.
