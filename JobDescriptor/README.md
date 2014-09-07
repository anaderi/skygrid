JOB DESCRIPTOR SPLIT METHODS
-------------
This is a class for splitting jobs in various ways.

Class **JobDescriptor** can create object by parsing JSON files and can split itself into smaller chunks

There are different strategies that should are implemented for splitting:
  - Split_equal() , creates N chunks out of job descriptor
  - Split_proportional(ArrayList l), creates N chunks of sizes proportional to integers p_i
  - Next(p), gives next job chunk of p items

JSON file should be always inside folder input/.


Run manually JobDescriptor
-------------

If you need to run and split manualy your own jobdescriptor:
* run `mvn package`
* create your input-file.json and put it inside input/ folder. (e.g. jd0.json)
* run `java -jar target/jobdescriptor-1.0.jar 0.json` (you can run it for more than one files if you want 
(e.g. `java -jar target/jobdescriptor-1.0.jar jd0.json jd1.json`)

(WARNING) currently with this jar file you can run only split_equal method.
