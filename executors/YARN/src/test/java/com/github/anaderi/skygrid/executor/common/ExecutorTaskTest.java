package com.github.anaderi.skygrid.executor.common;

import com.github.anaderi.skygrid.*;
import junit.framework.TestCase;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;

import java.io.IOException;

/**
 * Created by stromsund on 01.02.15.
 */
public class ExecutorTaskTest extends TestCase {
    public void testParsingElena() throws IOException {
        String elena = "{\n" +
                "  \"job\": {\n" +
                "    \"descriptor\": {\n" +
                "      \"app_container\": {\n" +
                "        \"name\": \"anaderi/ship-dev:0.0.15\", \n" +
                "        \"volume\": \"/opt/ship\"\n" +
                "      }, \n" +
                "      \"args\": {\n" +
                "        \"--nEvents\": 3, \n" +
                "        \"--output\": \"$OUTPUT_DIR/root\", \n" +
                "        \"--seed\": \"$JOB_ID\"\n" +
                "      }, \n" +
                "      \"cmd\": \"cd /opt/ship/FairShip/build; . ./config.sh; cp -r gconfig geometry python ..; export PYTHONPATH+=:/opt/ship/FairShip/build/python; ls -l $VMCWORKDIR/gconfig/; python macro/run_simScript.py\", \n" +
                "      \"cpu_per_container\": 1, \n" +
                "      \"email\": \"andrey.u@gmail.com\", \n" +
                "      \"env_container\": {\n" +
                "        \"app_volume\": \"$APP_CONTAINER\", \n" +
                "        \"name\": \"anaderi/ocean:latest\", \n" +
                "        \"output_volume\": \"$JOB_OUTPUT_DIR:/output\", \n" +
                "        \"workdir\": \"/opt/ship/FairShip/build\"\n" +
                "      }, \n" +
                "      \"job_id\": 20699, \n" +
                "      \"job_parent_id\": 5, \n" +
                "      \"job_super_id\": 5, \n" +
                "      \"max_memoryMB\": 1024, \n" +
                "      \"min_memoryMB\": 512, \n" +
                "      \"name\": \"SHIP-MC.test\", \n" +
                "      \"num_containers\": 48, \n" +
                "      \"status\": \"SUCCESS\"\n" +
                "    }, \n" +
                "    \"job_id\": \"54f4d30d2dc62576a36639db\", \n" +
                "    \"status\": \"pulled\"\n" +
                "  }, \n" +
                "  \"success\": true\n" +
                "}";
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        JobDescriptor task = mapper.readValue(elena, JobDescriptor.class);
        String serialized = mapper.writeValueAsString(task);
        System.out.println(task.toString());
    }

    public void testNoJob() throws IOException {
        String no_elena = "{\n" +
                "  \"success\": true\n" +
                "}";
        ObjectMapper mapper = new ObjectMapper();
        mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        JobDescriptor task = mapper.readValue(no_elena, JobDescriptor.class);
        System.out.println(task.toString());
    }
}
