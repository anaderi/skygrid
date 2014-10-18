Splitter
========

Splitter is a Java library, that splits a N-dimensional cube of tasks
into exactly M quite equal pieces. Split can be performed only along some direction,
so, the result of split is also a set of N-dimensional cubes.

Sum of volumes of that cubes is equal to the original cube volume.

Split algorithm after a countable amount of repetitions with random numbers had
the following distribution of disbalance between the biggest and the smallest
cubes:

    {1.0=6884, 2.0=603669, 3.0=26593}

Usage of the library looks like that:
```java
String input =
    "{\n" +
    "    \"name\": null,\n" +
    "    \"environments\": [\"anaderi/ocean\"],\n" +
    "    \"owner\": \"anaderi\",\n" +
    "    \"app\": \"my_app_container\",\n" +
    "    \"email\": \"andrey@none.com\",\n" +
    "    \"workdir\": \"/opt/ship/build\",\n" +
    "    \"cmd\": \"/opt/ship/python/muonShieldOptimization/g4ex.py\",\n" +
    "    \"args\": {\n" +
    "        \"default\": [\"--runNumber=1\", \"--nEvents=123\", \"--ecut=1\"],\n" +
    "        \"scaleArg\": [\n" +
    "            [\"nEvents\", \"SCALE\", 1200],\n" +
    "            [\"ecut\", \"SET\", [1, 10, 100]],\n" +
    "            [\"rcut\", \"RANGE\", [1, 100]]\n" +
    "        ]\n" +
    "    },\n" +
    "    \"num_containers\": 10,\n" +
    "    \"min_memoryMB\": 512,\n" +
    "    \"max_memoryMB\": 1024,\n" +
    "    \"cpu_per_container\": 1\n" +
    "}";
JobDescriptor jd = JobDescriptor.fromJsonString(input);
List<JobDescriptor> result = jd.split(2);
for (JobDescriptor subJobDescriptor : result) {
    System.out.println(subJobDescriptor);
}
```
And result is:

    {
      "name": null,
      "environments": ["anaderi/ocean"],
      "owner": "anaderi",
      "app": "my_app_container",
      "email": "andrey@none.com",
      "workdir": "/opt/ship/build",
      "cmd": "/opt/ship/python/muonShieldOptimization/g4ex.py",
      "args": {
        "default": ["--runNumber=1", "--nEvents=123", "--ecut=1"],
        "scaleArg": [
          ["ecut", "SET", [1, 10, 100]],
          ["rcut", "RANGE", [1, 50]],
          ["nEvents", "SCALE", 600]
        ]
      },
      "num_containers": 10,
      "min_memoryMB": 512,
      "max_memoryMB": 1024,
      "cpu_per_container": 1
    }

    {
      "name": null,
      "environments": ["anaderi/ocean"],
      "owner": "anaderi",
      "app": "my_app_container",
      "email": "andrey@none.com",
      "workdir": "/opt/ship/build",
      "cmd": "/opt/ship/python/muonShieldOptimization/g4ex.py",
      "args": {
        "default": ["--runNumber=1", "--nEvents=123", "--ecut=1"],
        "scaleArg": [  
          ["ecut", "SET", [1, 10, 100]],
          ["rcut", "RANGE", [51, 100]],
          ["nEvents", "SCALE", 600]
        ]
      },
      "num_containers": 10,
      "min_memoryMB": 512,
      "max_memoryMB": 1024,
      "cpu_per_container": 1
    }

Python bindings
---------------
I have also tested this code to work with Python (with a help of [Pyjnius](https://github.com/kivy/pyjnius)).
```python
"""
test_splitter.py - a module for testing com.github.anaderi.JobDescriptor
bindings with Python.

"""

import os
import sys

from jnius import autoclass


ORIGINAL_JD = """
{
    "name": null,
    "environments": ["anaderi/ocean"],
    "owner": "anaderi",
    "app": "my_app_container",
    "email": "andrey@none.com",
    "workdir": "/opt/ship/build",
    "cmd": "/opt/ship/python/muonShieldOptimization/g4ex.py",
    "args": {
        "default": ["--runNumber=1", "--nEvents=123", "--ecut=1"],
        "scaleArg": [
            ["nEvents", "SCALE", 1200],
            ["ecut", "SET", [1, 10, 100]],
            ["rcut", "RANGE", [1, 100]]
        ]
    },
    "num_containers": 10,
    "min_memoryMB": 512,
    "max_memoryMB": 1024,
    "cpu_per_container": 1
}
"""


def main():
    JobDescriptor = autoclass('com.github.anaderi.skygrid.JobDescriptor')
    descriptor = JobDescriptor.fromJsonString(ORIGINAL_JD)
    for sub_descriptor in descriptor.split(4):
        print sub_descriptor.toString()


if __name__ == '__main__':
    sys.exit(main())
```

And execution (Linux):

    $ CLASSPATH="target/splitter-1.0-SNAPSHOT.jar:\
        target/dependency/jackson-annotations-2.3.0.jar:\
        target/dependency/jackson-databind-2.3.3.jar:\
        target/dependency/jackson-core-2.3.3.jar:\
        target/dependency/junit-3.8.1.jar" \
    python test_splitter.py
    {"name":null,"environments":["anaderi/ocean"],"owner":"anaderi","app":"my_app_container","email":"andrey@none.com","workdir":"/opt/ship/build","cmd":"/opt/ship/python/muonShieldOptimization/g4ex.py","args":{"default":["--runNumber=1","--nEvents=123","--ecut=1"],"scaleArg":[["ecut","SET",[1,10,100]],["rcut","RANGE",[26,50]],["nEvents","SCALE",300]]},"num_containers":10,"min_memoryMB":512,"max_memoryMB":1024,"cpu_per_container":1}
    {"name":null,"environments":["anaderi/ocean"],"owner":"anaderi","app":"my_app_container","email":"andrey@none.com","workdir":"/opt/ship/build","cmd":"/opt/ship/python/muonShieldOptimization/g4ex.py","args":{"default":["--runNumber=1","--nEvents=123","--ecut=1"],"scaleArg":[["ecut","SET",[1,10,100]],["rcut","RANGE",[1,25]],["nEvents","SCALE",300]]},"num_containers":10,"min_memoryMB":512,"max_memoryMB":1024,"cpu_per_container":1}
    {"name":null,"environments":["anaderi/ocean"],"owner":"anaderi","app":"my_app_container","email":"andrey@none.com","workdir":"/opt/ship/build","cmd":"/opt/ship/python/muonShieldOptimization/g4ex.py","args":{"default":["--runNumber=1","--nEvents=123","--ecut=1"],"scaleArg":[["ecut","SET",[1,10,100]],["rcut","RANGE",[51,75]],["nEvents","SCALE",300]]},"num_containers":10,"min_memoryMB":512,"max_memoryMB":1024,"cpu_per_container":1}
    {"name":null,"environments":["anaderi/ocean"],"owner":"anaderi","app":"my_app_container","email":"andrey@none.com","workdir":"/opt/ship/build","cmd":"/opt/ship/python/muonShieldOptimization/g4ex.py","args":{"default":["--runNumber=1","--nEvents=123","--ecut=1"],"scaleArg":[["ecut","SET",[1,10,100]],["rcut","RANGE",[76,100]],["nEvents","SCALE",300]]},"num_containers":10,"min_memoryMB":512,"max_memoryMB":1024,"cpu_per_container":1}
    $
