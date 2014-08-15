package jobdescriptor;

import com.cedarsoftware.util.io.JsonWriter;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Random;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 *
 * @author Dimitris Sarigiannis
 */
public class JobDescriptor {

    private String jobDescriptorTxt;
    private JSONObject obj;
    
    public static int Split_equal_arg;
    public static ArrayList<Integer> Split_proportional_list;
    public static ArrayList<Integer> Split_next_args;
    
    private int nextCounter;
    private int currentJobDescriptor;
    
    public static void initArgs(){
        Split_equal_arg = 2;
        
        Split_proportional_list = new ArrayList<Integer>();
        Split_proportional_list.add(10);
        Split_proportional_list.add(90);
        
        Split_next_args = new ArrayList<Integer>();
        //Split_next_args.add(500);
        Split_next_args.add(300);
        //Split_next_args.add(200);
        //Split_next_args.add(1);
    }
    
    public JobDescriptor(String jobDescriptorName) throws FileNotFoundException, IOException, JSONException {
        
        this.nextCounter = 0; //for next sub-jobdescriptor
        this.currentJobDescriptor = 0;
        
        try {
            BufferedReader br = new BufferedReader(new FileReader(jobDescriptorName+this.currentJobDescriptor));
            this.jobDescriptorTxt = "";
            do {
                String temp = br.readLine();
                if (temp == null) {
                    break;
                }
                jobDescriptorTxt += temp;
            } while (true);
        } catch (FileNotFoundException fe) {
            System.err.println("File "+jobDescriptorName+this.currentJobDescriptor+" not found");
            System.exit(0);
        }

        this.obj = new JSONObject(this.jobDescriptorTxt);
    }
    
    
    /*
      Constructor only for testing 
    */
    public JobDescriptor(String jobDescriptorName,int i) throws FileNotFoundException, IOException, JSONException {
        
        this.nextCounter = 0; //for next sub-jobdescriptor
        this.currentJobDescriptor = 0;
        
        try {
            BufferedReader br = new BufferedReader(new FileReader(jobDescriptorName+i));
            this.jobDescriptorTxt = "";
            do {
                String temp = br.readLine();
                if (temp == null) {
                    break;
                }
                jobDescriptorTxt += temp;
            } while (true);
        } catch (FileNotFoundException fe) {
            System.err.println("File "+jobDescriptorName+i+" not found");
            System.exit(0);
        }

        this.obj = new JSONObject(this.jobDescriptorTxt);
    }

    /*
     Split the JobDescriptor file
     */
    public void Split_equal(int N) throws IOException, JSONException {

        if(this.getSCALE() % N != 0){
            System.err.println("Split_equal("+N+") is not not applicable.\nPlease change argument N and try again.");
            return;
        }
        
        Random RANDOM_SEED = new Random();
        int reduceSCALE = 0;

        for (int i = 1; i <= N; i++) {

            JSONObject subObj = new JSONObject();

            subObj.put("name", obj.get("name").toString());
            subObj.put("environments", obj.get("environments"));
            subObj.put("owner", obj.get("owner").toString());
            subObj.put("app", obj.get("app").toString());
            subObj.put("workdir", obj.get("workdir").toString());
            subObj.put("cmd", obj.get("cmd").toString());

            JSONObject subObj1 = new JSONObject(obj.get("args").toString());
            subObj1.put("default", subObj1.get("default"));

            JSONArray subArr; //e.g. ["nEvents","SCALE",1000]

            ArrayList<JSONArray> sublists = new ArrayList<JSONArray>(); //e.g. ["nEvents","SCALE",500]
            JSONArray sublist = new JSONArray(); //e.g. "nEvents"

            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(0).toString());
            sublist.put(subArr.get(0));
            sublist.put(subArr.get(1));
            
            sublist.put(new Integer((Integer) subArr.get(2) / N));
            //update jobdescriptor's SCALE
            reduceSCALE +=  new Integer((Integer) subArr.get(2) / N);
            
            sublists.add(sublist);
            sublist = new JSONArray();
            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(1).toString());
            sublist.put(subArr.get(0).toString());
            sublist.put(subArr.get(1).toString());
            sublist.put(subArr.get(2));
            sublists.add(sublist);
            sublist = new JSONArray();
            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(2).toString());
            sublist.put(subArr.get(0).toString());
            sublist.put(subArr.get(1).toString());
            sublist.put(subArr.get(2));
            sublists.add(sublist);
            sublist = new JSONArray();
            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(3).toString());
            sublist.put(subArr.get(0));
            sublist.put(RANDOM_SEED.nextInt(1000000000));
            sublists.add(sublist);
            subObj1.put("scaleArg", sublists);
            
            subObj.put("args", subObj1);

            subObj.put("num_containers", new Integer((Integer) obj.get("num_containers")));
            subObj.put("min_memoryMB", new Integer((Integer) obj.get("min_memoryMB")));
            subObj.put("max_memoryMB", new Integer((Integer) obj.get("max_memoryMB")));
            subObj.put("cpu_per_container", new Integer((Integer) obj.get("cpu_per_container")));

            writeJSONObjectToFile("sub-jobdescriptor" + i, subObj);

        }
        
        this.setSCALE(this.getSCALE()-reduceSCALE);
    }
    
    public void Split_proportional(ArrayList<Integer> l) throws JSONException, IOException{
        
        int sum = 0;
        for(Integer p : l){
            sum += p*10;
        }
        if(this.getSCALE() != sum){
            System.err.println("Split_propotional() is not not applicable.\nPlease change the proportions and try again.");
            return;
        }
        
        Random RANDOM_SEED = new Random();
        int reduceSCALE = 0;
        
        for (int i = 0; i < l.size(); i++) {

            JSONObject subObj = new JSONObject();

            subObj.put("name", obj.get("name").toString());
            subObj.put("environments", obj.get("environments"));
            subObj.put("owner", obj.get("owner").toString());
            subObj.put("app", obj.get("app").toString());
            subObj.put("workdir", obj.get("workdir").toString());
            subObj.put("cmd", obj.get("cmd").toString());

            JSONObject subObj1 = new JSONObject(obj.get("args").toString());
            subObj1.put("default", subObj1.get("default"));

            JSONArray subArr;

            ArrayList<JSONArray> sublists = new ArrayList<JSONArray>();
            JSONArray sublist = new JSONArray();

            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(0).toString());
            sublist.put(subArr.get(0));
            sublist.put(subArr.get(1));
            
            sublist.put(new Integer(((Integer) subArr.get(2) * l.get(i))/100)); //we assume that we have exact division always.
            reduceSCALE += (((Integer) subArr.get(2) * l.get(i))/100);
            
            sublists.add(sublist);
            sublist = new JSONArray();
            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(1).toString());
            sublist.put(subArr.get(0).toString());
            sublist.put(subArr.get(1).toString());
            sublist.put(subArr.get(2));
            sublists.add(sublist);
            sublist = new JSONArray();
            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(2).toString());
            sublist.put(subArr.get(0).toString());
            sublist.put(subArr.get(1).toString());
            sublist.put(subArr.get(2));
            sublists.add(sublist);
            sublist = new JSONArray();
            subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(3).toString());
            sublist.put(subArr.get(0));
            sublist.put(RANDOM_SEED.nextInt(1000000000));
            sublists.add(sublist);
            subObj1.put("scaleArg", sublists);
            
            subObj.put("args", subObj1);

            subObj.put("num_containers", new Integer((Integer) obj.get("num_containers")));
            subObj.put("min_memoryMB", new Integer((Integer) obj.get("min_memoryMB")));
            subObj.put("max_memoryMB", new Integer((Integer) obj.get("max_memoryMB")));
            subObj.put("cpu_per_container", new Integer((Integer) obj.get("cpu_per_container")));

            writeJSONObjectToFile("sub-jobdescriptor" + (i+1), subObj);

        }
        
        this.setSCALE(this.getSCALE()-reduceSCALE);
    }
    
    public void Split_next(int X) throws JSONException, IOException{
        
        if(X > this.getSCALE()){
            System.err.println("Split_next("+X+") has been canceled.\nPlease change the argument and try again.");
            return;
        }
        
        Random RANDOM_SEED = new Random();

        JSONObject subObj = new JSONObject();

        subObj.put("name", obj.get("name").toString());
        subObj.put("environments", obj.get("environments"));
        subObj.put("owner", obj.get("owner").toString());
        subObj.put("app", obj.get("app").toString());
        subObj.put("workdir", obj.get("workdir").toString());
        subObj.put("cmd", obj.get("cmd").toString());

        JSONObject subObj1 = new JSONObject(obj.get("args").toString());
        subObj1.put("default", subObj1.get("default"));

        JSONArray subArr;

        ArrayList<JSONArray> sublists = new ArrayList<JSONArray>();
        JSONArray sublist = new JSONArray();

        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(0).toString());
        sublist.put(subArr.get(0));
        sublist.put(subArr.get(1));

        //set new sub-jobdescriptor's SCALE
        sublist.put(new Integer(X));
        //update jobdescriptor's SCALE
        this.setSCALE(this.getSCALE()-X);

        sublists.add(sublist);
        sublist = new JSONArray();
        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(1).toString());
        sublist.put(subArr.get(0).toString());
        sublist.put(subArr.get(1).toString());
        sublist.put(subArr.get(2));
        sublists.add(sublist);
        sublist = new JSONArray();
        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(2).toString());
        sublist.put(subArr.get(0).toString());
        sublist.put(subArr.get(1).toString());
        sublist.put(subArr.get(2));
        sublists.add(sublist);
        sublist = new JSONArray();
        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(3).toString());
        sublist.put(subArr.get(0));
        sublist.put(RANDOM_SEED.nextInt(1000000000));
        sublists.add(sublist);
        subObj1.put("scaleArg", sublists);

        subObj.put("args", subObj1);

        subObj.put("num_containers", new Integer((Integer) obj.get("num_containers")));
        subObj.put("min_memoryMB", new Integer((Integer) obj.get("min_memoryMB")));
        subObj.put("max_memoryMB", new Integer((Integer) obj.get("max_memoryMB")));
        subObj.put("cpu_per_container", new Integer((Integer) obj.get("cpu_per_container")));

        writeJSONObjectToFile("sub-jobdescriptor" + (++this.nextCounter), subObj);
         //sub-jobdescriptor has been created successfully
    }

    public void writeJSONObjectToFile(String filename, JSONObject obj) throws IOException, JSONException {
        
        FileWriter file = new FileWriter(filename);
        
        file.write(JsonWriter.formatJson(obj.toString()));
        
        file.flush();
        file.close();
    }

    public int getSCALE() throws JSONException {
        JSONObject subObj = new JSONObject(obj.get("args").toString());
        JSONArray arr = new JSONArray(subObj.get("scaleArg").toString());
        JSONArray arr1 = new JSONArray(arr.getJSONArray(0).toString());
        return (Integer) arr1.get(2);
    }
    
    private void setSCALE(int newSCALE) throws JSONException, IOException{
        JSONObject subObj = new JSONObject();

        subObj.put("name", obj.get("name").toString());
        subObj.put("environments", obj.get("environments"));
        subObj.put("owner", obj.get("owner").toString());
        subObj.put("app", obj.get("app").toString());
        subObj.put("workdir", obj.get("workdir").toString());
        subObj.put("cmd", obj.get("cmd").toString());

        JSONObject subObj1 = new JSONObject(obj.get("args").toString());
        subObj1.put("default", subObj1.get("default"));

        JSONArray subArr;

        ArrayList<JSONArray> sublists = new ArrayList<JSONArray>();
        JSONArray sublist = new JSONArray();

        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(0).toString());
        sublist.put(subArr.get(0));
        sublist.put(subArr.get(1));
        sublist.put(newSCALE);
        sublists.add(sublist);
        sublist = new JSONArray();
        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(1).toString());
        sublist.put(subArr.get(0).toString());
        sublist.put(subArr.get(1).toString());
        sublist.put(subArr.get(2));
        sublists.add(sublist);
        sublist = new JSONArray();
        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(2).toString());
        sublist.put(subArr.get(0).toString());
        sublist.put(subArr.get(1).toString());
        sublist.put(subArr.get(2));
        sublists.add(sublist);
        sublist = new JSONArray();
        subArr = new JSONArray(subObj1.getJSONArray("scaleArg").get(3).toString());
        sublist.put(subArr.get(0));
        sublist.put("RANDOM_SEED");
        sublists.add(sublist);
        subObj1.put("scaleArg", sublists);

        subObj.put("args", subObj1);

        subObj.put("num_containers", new Integer((Integer) obj.get("num_containers")));
        subObj.put("min_memoryMB", new Integer((Integer) obj.get("min_memoryMB")));
        subObj.put("max_memoryMB", new Integer((Integer) obj.get("max_memoryMB")));
        subObj.put("cpu_per_container", new Integer((Integer) obj.get("cpu_per_container")));
        
        obj = subObj;
        
        writeJSONObjectToFile("jobdescriptor"+(++this.currentJobDescriptor), subObj); //updates jobdescriptor's file (creates new file to keep history-log)
    }

    public Integer getRANDOM_SEED() throws JSONException {
        JSONObject subObj = new JSONObject(obj.get("args").toString());
        JSONArray arr = new JSONArray(subObj.get("scaleArg").toString());
        JSONArray arr1 = new JSONArray(arr.getJSONArray(3).toString());
        return (Integer) arr1.get(1);
    }

    public ArrayList<String> getEnvironements() throws JSONException {
        ArrayList<String> environments = new ArrayList<String>();
        JSONArray arr = new JSONArray(obj.get("environments").toString());
        for (int i = 0; i < arr.length(); i++) {
            environments.add((String) arr.get(i));
        }
        return environments;
    }

    public ArrayList<Integer> getSET() throws JSONException {
        JSONObject subObj = new JSONObject(obj.get("args").toString());
        JSONArray arr = new JSONArray(subObj.get("scaleArg").toString());
        JSONArray arr1 = new JSONArray(arr.getJSONArray(1).toString()); //set
        JSONArray arr2 = new JSONArray(arr1.getJSONArray(2).toString());
        ArrayList<Integer> SET = new ArrayList<Integer>();
        for (int i = 0; i < arr2.length(); i++) {
            SET.add(arr2.getInt(i));
        }
        return SET;
    }

    public ArrayList<Integer> getRANGE() throws JSONException {
        JSONObject subObj = new JSONObject(obj.get("args").toString());
        JSONArray arr = new JSONArray(subObj.get("scaleArg").toString());
        JSONArray arr1 = new JSONArray(arr.getJSONArray(2).toString()); //set
        JSONArray arr2 = new JSONArray(arr1.getJSONArray(2).toString());
        ArrayList<Integer> RANGE = new ArrayList<Integer>();
        for (int i = 0; i < arr2.length(); i++) {
            RANGE.add(arr2.getInt(i));
        }
        return RANGE;
    }

    public String getOwner() throws JSONException {
        return obj.get("owner").toString();
    }

    public String getApp() throws JSONException {
        return obj.get("app").toString();
    }

    public String getWorkDir() throws JSONException {
        return obj.get("workdir").toString();
    }

    public String getCmd() throws JSONException {
        return obj.get("cmd").toString();
    }

    public String getName() throws JSONException {
        return obj.get("name").toString();
    }

    public int getNumberOfContainers() throws JSONException {
        return (Integer) obj.get("num_containers");
    }

    public int getMinMemoryMB() throws JSONException {
        return (Integer) obj.get("min_memoryMB");
    }

    public int getMaxMemoryMB() throws JSONException {
        return (Integer) obj.get("max_memoryMB");
    }

    public int getCPUperContainer() throws JSONException {
        return (Integer) obj.get("cpu_per_container");
    }

    public int getCurrentJobDescriptor() {
        return currentJobDescriptor;
    }
    
    

    /**
     * @param args the command line arguments
     * @throws InterruptedException 
     * @throws SecurityException 
     * @throws NoSuchFieldException 
     * @throws IllegalAccessException 
     * @throws IllegalArgumentException 
     */
    public static void main(String[] args) throws IOException, JSONException, InterruptedException, IllegalArgumentException, IllegalAccessException, NoSuchFieldException, SecurityException {
        //TODO
        JobDescriptor jd = new JobDescriptor("jobdescriptor");
        
        initArgs();
        
        jd.Split_equal(Split_equal_arg);

	Jeeves jeeves = new Jeeves(jd);
        
        /*
        jd.Split_proportional(Split_proportional_list);
        */
       
        /*
        jd.Split_next(Split_next_args.get(0));
        jd.Split_next(Split_next_args.get(1));
        jd.Split_next(Split_next_args.get(2));
        jd.Split_next(Split_next_args.get(3));
        */
        
    }

}

