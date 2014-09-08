package jobdescriptor;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import static jobdescriptor.JobDescriptor.getInputFiles;
import static jobdescriptor.JobDescriptor.initDir;
import org.json.JSONException;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

/**
 *
 * @author Dimitris Sarigiannis
 */
public class JobDescriptorTest {

    private ArrayList<JobDescriptor> JDs;
    private ArrayList<JobDescriptor> subjds;

    public JobDescriptorTest() {
    }

    @BeforeClass
    public static void setUpClass() {
        initDir(new File("output"));
        JobDescriptor.initArgs();
    }

    @AfterClass
    public static void tearDownClass() {
    }

    @Before
    public void setUp() throws IOException, FileNotFoundException, JSONException {
        System.out.println("setUp");
        JDs = new ArrayList<JobDescriptor>();
        ArrayList<String> inputFiles = getInputFiles();
        for(String jsonFile : inputFiles){
            JDs.add(new JobDescriptor(jsonFile));
        }
    }

    @After
    public void tearDown() {
        System.out.println("tearDown");
    }

    /**
     * Test of Split_equal method, of class JobDescriptor.
     */
    @Test
    public void testSplit_equal() throws Exception {
        System.out.println("Split_equal");
        
        for(JobDescriptor jd : JDs){
            jd.Split_equal();
        }   
        
    }
    
    /**
     * Test of Split_proportional method, of class JobDescriptor.
     * @throws java.lang.Exception
     */
    @Test
    public void testSplit_proportional() throws Exception {
        System.out.println("Split_proportional");

        for(JobDescriptor jd : JDs){
            jd.Split_proportional(JobDescriptor.Split_proportional_list);
        }
        
    }
    
    /**
     * Test of Split_next method, of class JobDescriptor.
     * @throws java.lang.Exception
     */
    @Test
    public void testSplit_next() throws Exception {
        System.out.println("Split_next");
        
        JobDescriptor jd = new JobDescriptor("input/jobdescriptor0.json");
        jd.Split_next(JobDescriptor.Split_next_args.get(0)); 
    }
    
}

