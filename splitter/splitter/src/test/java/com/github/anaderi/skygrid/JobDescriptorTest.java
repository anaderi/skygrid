package com.github.anaderi.skygrid;

import junit.framework.TestCase;

import java.io.IOException;
import java.util.List;

public class JobDescriptorTest extends TestCase {
    public void testJsonReading() throws Exception {
        JobDescriptor jd = getJobDescriptor();
        String[] obligatory_pieces = {"name", "null", "environments", "anaderi/ocean",
            "owner", "anaderi", "app", "my_app_container", "email", "andrey@none.com",
            "workdir", "/opt/ship/build", "cmd", "/opt/ship/python/muonShieldOptimization/g4ex.py",
            "args", "default", "--runNumber=1", "--nEvents=123", "--ecut=1",
            "scaleArg", "nEvents", "SCALE", "1200", "ecut", "SET", "1", "10", "100",
            "rcut", "RANGE", "num_containers", "min_memoryMB", "512", "max_memoryMB", "1024",
            "cpu_per_container"};
        String serializedJobDescriptor = jd.toString();
        for (String piece : obligatory_pieces) {
            assertTrue(serializedJobDescriptor.contains(piece));
        }
    }

    public void testJsonSplitting() throws Exception {
        JobDescriptor jd = getJobDescriptor();
        List<JobDescriptor> result = jd.split(2);
        assertEquals(2, result.size());
        for (JobDescriptor subJobDescriptor : result) {
            assertTrue(subJobDescriptor.toString().contains("600"));
        }
    }

    public void testDescriptorsVolume() throws Exception {
        JobDescriptor jd = getJobDescriptor();
        assertEquals(300, jd.volume());
    }

    private JobDescriptor getJobDescriptor() throws JobDescriptor.JobDescriptorFormatException, IOException {
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
        return JobDescriptor.fromJsonString(input);
    }
}
