package com.github.anaderi.skygrid.executor.wooster;

import com.github.anaderi.skygrid.JobDescriptor;
import junit.framework.TestCase;

public class JobDescriptorProcessingQueueTest extends TestCase {
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
    private static final String jd2 =
            "{" +
                    "\"name\":null," +
                    "\"environments\":[\"anaderi/ocean\"]," +
                    "\"owner\":\"anaderi\"," +
                    "\"app\":\"my_app_container\"," +
                    "\"email\":\"xni@none.com\"," +
                    "\"workdir\":\"/opt/ship/build\"," +
                    "\"cmd\":\"/opt/ship/python/muonShieldOptimization/g4ex.py\"," +
                    "\"args\":{\n" +
                        "\"default\":[\"--runNumber=1\",\"--nEvents=123\",\"--ecut=1\"]," +
                        "\"scaleArg\":[" +
                        "[\"nEvents\",\"SCALE\",12000]," +
                        "[\"ecut\",\"SET\",[1,10,100]]," +
                        "[\"rcut\",\"RANGE\",[1,100]]" +
                        "]" +
                    "}," +
                    "\"num_containers\":10," +
                    "\"min_memoryMB\":512," +
                    "\"max_memoryMB\":1024," +
                    "\"cpu_per_container\":1" +
                    "}";

    private JobDescriptorProcessingQueue queue_;

    @Override
    public void setUp() {
        queue_ = new JobDescriptorProcessingQueue();
    }

    public void testQueueAppending() throws Exception {
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd1));
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd2));
    }

    public void testQueueEmpty() throws Exception {
        assertEquals(false, queue_.HasUpcomingTasks());
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd2));
        assertEquals(true, queue_.HasUpcomingTasks());
    }

    public void testGetTask() throws Exception {
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd1));
        assertEquals(JobDescriptor.fromJsonString(jd1), queue_.GetNextTask());
    }

    public void testFindJobDescriptorIndex() throws Exception {
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd1));
        assertEquals(0, queue_.FindJobDescriptorIndex(JobDescriptor.fromJsonString(jd1)));
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd2));
        assertEquals(0, queue_.FindJobDescriptorIndex(JobDescriptor.fromJsonString(jd1)));
        assertEquals(1, queue_.FindJobDescriptorIndex(JobDescriptor.fromJsonString(jd2)));
    }

    public void testSimpleBadWorkflow() throws Exception {
        assertFalse(queue_.HasUpcomingTasks());
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd1));
        assertTrue(queue_.HasUpcomingTasks());
        JobDescriptor task = queue_.GetNextTask();
        assertFalse(queue_.HasUpcomingTasks());
        queue_.MarkJobDescriptorAsFailed(JobDescriptor.fromJsonString(jd1));
        assertTrue(queue_.HasUpcomingTasks());
        assertFalse(queue_.IsCompletedSuccsessfully());
    }

    public void testSimpleGoodWorkflow() throws Exception {
        assertFalse(queue_.HasUpcomingTasks());
        queue_.AppendJobDescriptor(JobDescriptor.fromJsonString(jd1));
        assertTrue(queue_.HasUpcomingTasks());
        JobDescriptor task = queue_.GetNextTask();
        assertFalse(queue_.HasUpcomingTasks());
        queue_.MarkJobDescriptorAsCompleted(JobDescriptor.fromJsonString(jd1));
        assertFalse(queue_.HasUpcomingTasks());
        assertTrue(queue_.IsCompletedSuccsessfully());
    }
}