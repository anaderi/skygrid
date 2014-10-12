package com.github.anaderi.skygrid;

import junit.framework.TestCase;

public class JobDescriptorTest extends TestCase {
    public void testJsonReading() throws Exception {
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
                "            [\"nEvents\", \"SCALE\", 1000],\n" +
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
    }
}
