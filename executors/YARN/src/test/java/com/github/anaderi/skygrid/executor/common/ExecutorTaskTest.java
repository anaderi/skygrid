package com.github.anaderi.skygrid.executor.common;

import junit.framework.TestCase;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;

import java.io.IOException;

/**
 * Created by stromsund on 01.02.15.
 */
public class ExecutorTaskTest extends TestCase {
    private static final String jd1 =
            "{" +
                    "\"name\":null," +
                    "\"environments\":[\"anaderi/ocean\"]," +
                    "\"owner\":\"anaderi\"," +
                    "\"app\":\"my_app_container\"," +
                    "\"email\":\"andrey@none.com\"," +
                    "\"workdir\":\"/opt/ship/build\"," +
                    "\"cmd\":\"/opt/ship/python/muonShieldOptimization/g4ex.py\"," +
                    "\"args\":{\n" +
                    "\"default\":[\"--runNumber=1\",\"--nEvents=123\",\"--ecut=1\"]," +
                    "\"scaleArg\":[" +
                    "[\"nEvents\",\"SCALE\",1200]," +
                    "[\"ecut\",\"SET\",[1,10,100]]," +
                    "[\"rcut\",\"RANGE\",[1,100]]" +
                    "]" +
                    "}," +
                    "\"num_containers\":10," +
                    "\"min_memoryMB\":512," +
                    "\"max_memoryMB\":1024," +
                    "\"cpu_per_container\":1" +
                    "}";

    public void testParsing() throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        ExecutionTask task = mapper.readValue(jd1, ExecutionTask.class);
        assertEquals("my_app_container", task.getApp());
        assertEquals(1, task.getEnvironments().size());
        assertEquals("anaderi/ocean", task.getEnvironments().get(0));
        assertEquals("/opt/ship/python/muonShieldOptimization/g4ex.py", task.getCmd());
    }
}
