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
