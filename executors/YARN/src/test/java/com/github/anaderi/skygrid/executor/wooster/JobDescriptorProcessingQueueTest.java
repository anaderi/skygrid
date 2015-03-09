package com.github.anaderi.skygrid.executor.wooster;

import com.github.anaderi.skygrid.executor.common.JobDescriptor;
import junit.framework.TestCase;
import org.codehaus.jackson.map.ObjectMapper;

import java.io.IOException;

public class JobDescriptorProcessingQueueTest extends TestCase {
    private static final String jd1 = "{\n" +
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
    private static final String jd2 = "{\n" +
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
        "    \"job_id\": \"54f4d30d2dc62576a36639dc\", \n" +
        "    \"status\": \"pulled\"\n" +
        "  }, \n" +
        "  \"success\": true\n" +
        "}";

    private JobDescriptorProcessingQueue queue_;

    @Override
    public void setUp() {
        queue_ = new JobDescriptorProcessingQueue();
    }

    private JobDescriptor jdFromString(String jd) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        return (JobDescriptor)objectMapper.readValue(jd, JobDescriptor.class);
    }

    public void testQueueAppending() throws Exception {
        queue_.AppendJobDescriptor(jdFromString(jd1));
        queue_.AppendJobDescriptor(jdFromString(jd2));
    }

    public void testQueueEmpty() throws Exception {
        assertEquals(false, queue_.HasUpcomingTasks());
        queue_.AppendJobDescriptor(jdFromString(jd2));
        assertEquals(true, queue_.HasUpcomingTasks());
    }

    public void testGetTask() throws Exception {
        queue_.AppendJobDescriptor(jdFromString(jd1));
        assertEquals(jdFromString(jd1), queue_.GetNextTask());
    }

    public void testSimpleBadWorkflow() throws Exception {
        assertFalse(queue_.HasUpcomingTasks());
        queue_.AppendJobDescriptor(jdFromString(jd1));
        assertTrue(queue_.HasUpcomingTasks());
        JobDescriptor task = queue_.GetNextTask();
        assertFalse(queue_.HasUpcomingTasks());
        queue_.MarkJobDescriptorAsFailed(jdFromString(jd1));
        assertTrue(queue_.HasUpcomingTasks());
        assertFalse(queue_.IsCompletedSuccsessfully());
    }

    public void testSimpleGoodWorkflow() throws Exception {
        assertFalse(queue_.HasUpcomingTasks());
        queue_.AppendJobDescriptor(jdFromString(jd1));
        assertTrue(queue_.HasUpcomingTasks());
        JobDescriptor task = queue_.GetNextTask();
        assertFalse(queue_.HasUpcomingTasks());
        queue_.MarkJobDescriptorAsCompleted(jdFromString(jd1));
        assertFalse(queue_.HasUpcomingTasks());
        assertTrue(queue_.IsCompletedSuccsessfully());
    }
}