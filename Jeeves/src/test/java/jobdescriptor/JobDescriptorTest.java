package jobdescriptor;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import org.json.JSONException;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author Dimitris Sarigiannis
 */
public class JobDescriptorTest {

    private JobDescriptor jd;
    ArrayList<JobDescriptor> subjds;

    public JobDescriptorTest() {
    }

    @BeforeClass
    public static void setUpClass() {
        JobDescriptor.initArgs();
    }

    @AfterClass
    public static void tearDownClass() {
    }

    @Before
    public void setUp() throws IOException, FileNotFoundException, JSONException {
        System.out.println("setUp");
        jd = new JobDescriptor("jobdescriptor");
    }

    @After
    public void tearDown() {
        jd = null;
        System.out.println("tearDown");
    }

    /**
     * Test of Split_equal method, of class JobDescriptor.
     */
    @Test
    public void testSplit_equal() throws Exception {
        System.out.println("Split_equal");
        
        int N = JobDescriptor.Split_equal_arg;
        
        jd.Split_equal(N);

        createSubDescriptors(N);
        
        testEqualSCALE();
        testRANDOM_SEED();
        testEnvironments();
        testName();
        testOwner();
        testApp();
        testWorkDir();
        testCmd();
        testNumberOfContainers();
        testMinMemoryMB();
        testMaxMemoryMB();
        testCPUperContainer();
        testSET();
        testEqualandProportionalRANGE();
    }
    
    /**
     * Test of Split_proportional method, of class JobDescriptor.
     * @throws java.lang.Exception
     */
    @Test
    public void Split_proportional() throws Exception {
        System.out.println("Split_proportional");

        testSplitProportionalListArgument();
        
        jd.Split_proportional(JobDescriptor.Split_proportional_list);

        createSubDescriptors(JobDescriptor.Split_proportional_list.size());

        testProportionalSCALE();
        testRANDOM_SEED();
        testEnvironments();
        testName();
        testOwner();
        testApp();
        testWorkDir();
        testCmd();
        testNumberOfContainers();
        testMinMemoryMB();
        testMaxMemoryMB();
        testCPUperContainer();
        testSET();
        testEqualandProportionalRANGE();
    }
    
    /**
     * Test of Split_next method, of class JobDescriptor.
     * @throws java.lang.Exception
     */
    @Test
    public void Split_next() throws Exception {
        System.out.println("Split_next");
        
        testSplitNextArgument();
        
        jd.Split_next(JobDescriptor.Split_next_args.get(0));

        createSubDescriptors(1);

        testNextSCALE();
        testRANDOM_SEED();
        testEnvironments();
        testName();
        testOwner();
        testApp();
        testWorkDir();
        testCmd();
        testNumberOfContainers();
        testMinMemoryMB();
        testMaxMemoryMB();
        testCPUperContainer();
        testSET();
        testNextRANGE();
    }

    public void createSubDescriptors(int N) throws IOException, FileNotFoundException, JSONException {
        subjds = new ArrayList<JobDescriptor>();
        for (int i = 1; i <= N; i++) {
            subjds.add(new JobDescriptor("output/sub-jobdescriptor",i));
        }
    }
    
    public void testSplitProportionalListArgument() throws JSONException{
        int sum = 0;
        for(Integer p : JobDescriptor.Split_proportional_list){
            sum += p*10;
        }
        assertEquals(jd.getSCALE(),sum);
    }
    
    public void testSplitNextArgument() throws JSONException{
        assertTrue(0 < JobDescriptor.Split_next_args.get(0) && JobDescriptor.Split_next_args.get(0) <= jd.getSCALE());
    }
    
    /*
     sum of sub-jobdestcriptors SCALE must be equal to jobdescriptor SCALE
     */
    public void testEqualSCALE() throws JSONException, IOException {
        //test if sum of equal splitted parts is equal to jobdescriptors scale
        int sumSCALE = 0;
        for (JobDescriptor subjd : subjds) {
            sumSCALE += subjd.getSCALE();
        }
        JobDescriptor previousJobDescriptor = new JobDescriptor("jobdescriptor" , (jd.getCurrentJobDescriptor()-1) );
        assertEquals(previousJobDescriptor.getSCALE(), sumSCALE);
    }
    
    /*
     sum of sub-jobdestcriptors SCALE must be equal to jobdescriptor SCALE
     */
    public void testProportionalSCALE() throws JSONException, IOException {
        //test if sum of equal splitted parts is equal to jobdescriptors scale
        int sumSCALE = 0;
        for (JobDescriptor subjd : subjds) {
            sumSCALE += subjd.getSCALE();
        }
        JobDescriptor previousJobDescriptor = new JobDescriptor("jobdescriptor" , (jd.getCurrentJobDescriptor()-1) );
        assertEquals(previousJobDescriptor.getSCALE(), sumSCALE);
    }
    
    /*
     sum of sub-jobdestcriptors SCALE must be equal to jobdescriptor SCALE
     */
    public void testNextSCALE() throws JSONException, IOException {
        assertTrue(1 <= subjds.get(0).getSCALE() && subjds.get(0).getSCALE() <= jd.getSCALE());
        
        int expectedSCALE = new JobDescriptor("jobdescriptor").getSCALE();
        assertEquals(expectedSCALE, subjds.get(0).getSCALE() + jd.getSCALE());
    }

    /*
     RANDOM_SEED must be within range [0,10^9)
     */
    public void testRANDOM_SEED() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertTrue(0 <= subjd.getRANDOM_SEED() && subjd.getRANDOM_SEED() < 1000000000);
        }
    }

    public void testEnvironments() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            int env_i = 0;
            for (String env : subjd.getEnvironements()) {
                assertEquals(jd.getEnvironements().get(env_i), env);
                env_i++;
            }
        }
    }

    public void testSET() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            int set_i = 0;
            for (Integer set : subjd.getSET()) {
                assertEquals(jd.getSET().get(set_i), set);
                set_i++;
            }
        }
    }

    public void testNextRANGE() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            int range_i = 0;
            for (Integer range : subjd.getRANGE()) {
                assertEquals(jd.getRANGE().get(range_i), range);
                range_i++;
            }
        }
    }
    
     public void testEqualandProportionalRANGE() throws JSONException {
        int initMax = jd.getRANGE().get(1);
        int initMin = jd.getRANGE().get(0);
        int initRange = initMax - initMin + 1;
        int sumRange = 0;
        for (JobDescriptor subjd : subjds) {
            int max = subjd.getRANGE().get(1);
            int min = subjd.getRANGE().get(0);
            sumRange += max - min + 1;
        }
        assertEquals(initRange, sumRange);
    }

    public void testName() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getName(), subjd.getName());
        }
    }

    public void testOwner() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getOwner(), subjd.getOwner());
        }
    }

    public void testApp() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getApp(), subjd.getApp());
        }
    }

    public void testWorkDir() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getWorkDir(), subjd.getWorkDir());
        }
    }

    public void testCmd() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getCmd(), subjd.getCmd());
        }
    }

    public void testNumberOfContainers() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getNumberOfContainers(), subjd.getNumberOfContainers());
        }
    }

    public void testMinMemoryMB() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getMinMemoryMB(), subjd.getMinMemoryMB());
        }
    }

    public void testMaxMemoryMB() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getMaxMemoryMB(), subjd.getMaxMemoryMB());
        }
    }

    public void testCPUperContainer() throws JSONException {
        for (JobDescriptor subjd : subjds) {
            assertEquals(jd.getCPUperContainer(), subjd.getCPUperContainer());
        }
    }

}

