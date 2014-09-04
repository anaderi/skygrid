JOB DESCRIPTOR SPLIT METHODS
-------------
This is a class for splitting jobs in various ways.

Class JobDescriptor can create object by parsing JSON files and can split itself into smaller chunks

There are different strategies that should are implemented for splitting:
  - Split_equal(integer N) , creates N chunks out of job descriptor
  - Split_proportional(ArrayList l), creates N chunks of sizes proportional to integers p_i
  - Next(p), gives next job chunk of p items

jobdescriptor0 JSON file is always the initial input-jobdescriptor.
