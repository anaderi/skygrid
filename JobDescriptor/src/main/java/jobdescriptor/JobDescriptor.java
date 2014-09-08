package jobdescriptor;

import com.cedarsoftware.util.io.JsonWriter;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Random;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.net.UnknownHostException;
import java.util.HashMap;
import java.util.Iterator;

/**
 *
 * @author Dimitris Sarigiannis
 */
public class JobDescriptor {

    private String jobDescriptorTxt;
    private JSONObject obj;
    private int jobID;

    public static int Split_equal_arg;
    public static ArrayList<Integer> Split_proportional_list;
    public static ArrayList<Integer> Split_next_args;

    private int nextCounter;
    private int currentJobDescriptor;

    private final String outputFolder;

    public static void initArgs() {

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
        
        this.outputFolder = "output"+jobDescriptorName.replace(".json", "").replace("input", "");
        File outputDir = new File(outputFolder.replace("input", "output"));
        
        createOutputFolder(new File("output"));
        createOutputFolder(outputDir);

        this.nextCounter = 0; //for next sub-jobdescriptor
        this.currentJobDescriptor = 0;

        try {
            BufferedReader br = new BufferedReader(new FileReader(jobDescriptorName));
            this.jobDescriptorTxt = "";
            do {
                String temp = br.readLine();
                if (temp == null) {
                    break;
                }
                jobDescriptorTxt += temp;
            } while (true);
        } catch (FileNotFoundException fe) {
            System.err.println("File " + jobDescriptorName + this.currentJobDescriptor + " not found");
            System.exit(0);
        }

        this.obj = new JSONObject(this.jobDescriptorTxt);
        if (obj.has("job_id")) {
            if(obj.get("job_id").equals(null)){
                jobID = 0;
            }else
            jobID = obj.getInt("job_id");
        }
    }

    /*
     Constructor only for testing 
     */
    public JobDescriptor(String jobDescriptorName, int i) throws FileNotFoundException, IOException, JSONException {

        this.outputFolder = "output"+jobDescriptorName.replace(".json", "").replace("input", "");
        this.nextCounter = 0; //for next sub-jobdescriptor
        this.currentJobDescriptor = 0;

        try {
            BufferedReader br = new BufferedReader(new FileReader(jobDescriptorName));
            this.jobDescriptorTxt = "";
            do {
                String temp = br.readLine();
                if (temp == null) {
                    break;
                }
                jobDescriptorTxt += temp;
            } while (true);
        } catch (FileNotFoundException fe) {
            System.err.println("File " + jobDescriptorName + i + " not found");
            System.exit(0);
        }

        this.obj = new JSONObject(this.jobDescriptorTxt);
        if (obj.has("job_id")) {
            if(obj.get("job_id").equals(null)){
                jobID = 0;
            }else
            jobID = obj.getInt("job_id");
        }
    }

    private void createOutputFolder(File theDir) {

        if (!theDir.exists()) {
            try {
                theDir.mkdir();
            } catch (SecurityException se) {
                System.exit(1);
            }
        }
    }

    public static void initDir(File path) {
    if (path == null)
        return;
    if (path.exists())
    {
        for(File f : path.listFiles())
        {
            if(f.isDirectory()) 
            {
                initDir(f);
                f.delete();
            }
            else
            {
                f.delete();
            }
        }
        path.delete();
    }
    }

    private int getRANGELength(JSONArray arr) throws JSONException {
        return arr.getInt(1) - arr.getInt(0) + 1;
    }

    private int getSETLength(JSONArray arr) {
        return arr.length();
    }

    /*
     Split the JobDescriptor file
     */
    public boolean Split_equal() throws JSONException, IOException {

        JSONObject subObj = new JSONObject();

        //set job-IDs
        if (obj.has("job_id")) {
            subObj.put("job_parent_id", obj.get("job_id"));
            subObj.put("job_super_id", obj.get("job_id"));
        }

        //find split-way and how many splits
        HashMap<String, Integer> scaleArgHash = new HashMap<String, Integer>();
        HashMap<String, String> scaleArgKeyHash = new HashMap<String, String>();
        JSONArray scaleArgArr = obj.getJSONObject("args").getJSONArray("scaleArg");
        JSONArray getRANGEArr = null;
        JSONArray getSETArr = null;
        for (int i = 0; i < scaleArgArr.length(); i++) {
            if (scaleArgArr.getJSONArray(i).get(1).equals("RANGE")) {
                getRANGEArr = scaleArgArr.getJSONArray(i).getJSONArray(2);
                scaleArgHash.put(scaleArgArr.getJSONArray(i).get(1).toString(), getRANGELength(scaleArgArr.getJSONArray(i).getJSONArray(2)));
                scaleArgKeyHash.put("RANGE", scaleArgArr.getJSONArray(i).get(0).toString());
            } else if (scaleArgArr.getJSONArray(i).get(1).equals("SET")) {
                getSETArr = scaleArgArr.getJSONArray(i).getJSONArray(2);
                scaleArgHash.put(scaleArgArr.getJSONArray(i).get(1).toString(), getSETLength(scaleArgArr.getJSONArray(i).getJSONArray(2)));
                scaleArgKeyHash.put("SET", scaleArgArr.getJSONArray(i).get(0).toString());
            } else if (scaleArgArr.getJSONArray(i).get(1).equals("SCALE")) {
                scaleArgHash.put(scaleArgArr.getJSONArray(i).get(1).toString(), scaleArgArr.getJSONArray(i).getInt(2));
                scaleArgKeyHash.put("SCALE", scaleArgArr.getJSONArray(i).get(0).toString());
            } else if (scaleArgArr.getJSONArray(i).get(1).equals("RANDOM_SEED")) {
                scaleArgKeyHash.put("RANDOM_SEED", scaleArgArr.getJSONArray(i).get(0).toString());
            }
        }

        //define initial N
        int N;
        if (scaleArgHash.containsKey("RANGE")) {
            N = (scaleArgHash.containsKey("RANGE") ? scaleArgHash.get("RANGE") : 1);
            if (N > scaleArgHash.get("SCALE")) {
                return false;
            }
            if (scaleArgHash.containsKey("SET")) {
                if (N * scaleArgHash.get("SET") <= scaleArgHash.get("SCALE")) {
                    N *= scaleArgHash.get("SET");
                }
            }
        } else if (scaleArgHash.containsKey("SCALE")) {
            N = scaleArgHash.get("SCALE");
        } else {
            //unable to split to smaller chunks
            return false;
        }
        //optimise N
        int scaleToEachSubJD = -1;
        int scaleBalance = -1;
        if (scaleArgHash.containsKey("SCALE")) {
            scaleToEachSubJD = scaleArgHash.get("SCALE") / N;
            if (scaleToEachSubJD < 1) {
                return false;
            }
            scaleBalance = scaleArgHash.get("SCALE") % N;
        }

        int start = 1;
        int SET_pos = 0; //init SET
        int RANGE_pos = scaleArgHash.containsKey("RANGE") ? getRANGEArr.getInt(0) : 0; //init RANGE
        for (int subJd_pos = start; subJd_pos <= N; subJd_pos++) {
            Iterator<String> JSON_keys = obj.keys();
            while (JSON_keys.hasNext()) {
                String currentKey = JSON_keys.next();
                if (currentKey.equals("args")) {
                    JSONObject args = obj.getJSONObject("args");
                    Iterator<String> argsKeys = args.keys();
                    JSONObject subArgs = new JSONObject();
                    while (argsKeys.hasNext()) {
                        String currentArgsKey = argsKeys.next();
                        if (currentArgsKey.equals("scaleArg")) {
                            if (scaleArgHash.containsKey("SCALE")) {
                                subArgs.put(scaleArgKeyHash.get("SCALE"), scaleToEachSubJD + (((scaleBalance--) > 0) ? 1 : 0));
                            }
                            if (scaleArgHash.containsKey("RANGE")) {
                                subArgs.put(scaleArgKeyHash.get("RANGE"), RANGE_pos++);
                            }
                            if (scaleArgHash.containsKey("SET")) {
                                subArgs.put(scaleArgKeyHash.get("SET"), getSETArr.get(SET_pos++));
                            }
                            if (scaleArgKeyHash.containsKey("RANDOM_SEED")) {
                                Random RANDOM_SEED = new Random();
                                subArgs.put(scaleArgKeyHash.get("RANDOM_SEED"), RANDOM_SEED.nextInt(1000000000));
                            }
                        } else {
                            if (args.get(currentArgsKey) instanceof String) {
                                subArgs.put(currentArgsKey, args.get(currentArgsKey));
                            } else if (args.get(currentArgsKey) instanceof Integer) {
                                subArgs.put(currentArgsKey, args.getInt(currentArgsKey));
                            }
                        }
                    }
                    subObj.put("args", subArgs);

                } else {
                    if (obj.get(currentKey) instanceof String) {
                        subObj.put(currentKey, obj.get(currentKey));
                    } else if (obj.get(currentKey) instanceof Integer) {
                        subObj.put(currentKey, obj.getInt(currentKey));
                    }
                }
            }
            if (obj.has("job_id")) {
                subObj.put("job_id", jobID + subJd_pos);
            }
            writeJSONObjectToFile("sub-jobdescriptor" + subJd_pos, subObj);
            if (scaleArgHash.containsKey("SET")) {
                if (SET_pos > getSETArr.length() - 1) {
                    SET_pos = 0;
                }
            }
            if (scaleArgHash.containsKey("RANGE")) {
                if (RANGE_pos > getRANGEArr.getInt(1)) {
                    RANGE_pos = getRANGEArr.getInt(0);
                }
            }
        }
        return true;
    }

    public void Split_proportional(ArrayList<Integer> l) throws JSONException, IOException {

        HashMap<String, Integer> scaleArgHash = new HashMap<String, Integer>();
        HashMap<String, String> scaleArgKeyHash = new HashMap<String, String>();
        JSONArray scaleArgArr = obj.getJSONObject("args").getJSONArray("scaleArg");
        for (int i = 0; i < scaleArgArr.length(); i++) {
            if (scaleArgArr.getJSONArray(i).get(1).equals("SCALE")) {
                scaleArgHash.put(scaleArgArr.getJSONArray(i).get(1).toString(), scaleArgArr.getJSONArray(i).getInt(2));
                scaleArgKeyHash.put("SCALE", scaleArgArr.getJSONArray(i).get(0).toString());
            } else if (scaleArgArr.getJSONArray(i).get(1).equals("RANDOM_SEED")) {
                scaleArgKeyHash.put("RANDOM_SEED", scaleArgArr.getJSONArray(i).get(0).toString());
            }
        }
        
        double sum = 0;
        for (Integer p : l) {
            sum += p * scaleArgHash.get("SCALE") * 0.01;
        }
        if (scaleArgHash.get("SCALE") != sum) {
            System.err.println("Split_propotional() is not not applicable.\nPlease change the proportions and try again.");
            return;
        }

        JSONObject subObj = new JSONObject();

        //set job-IDs
        if (obj.has("job_id")) {
            subObj.put("job_parent_id", obj.get("job_id"));
            subObj.put("job_super_id", obj.get("job_id"));
        }

        for (int i = 0; i < l.size(); i++) {

            Iterator<String> JSON_keys = obj.keys();
            while (JSON_keys.hasNext()) {
                String currentKey = JSON_keys.next();
                if (currentKey.equals("args")) {
                    JSONObject args = obj.getJSONObject("args");
                    Iterator<String> argsKeys = args.keys();
                    JSONObject subArgs = new JSONObject();
                    while (argsKeys.hasNext()) {
                        String currentArgsKey = argsKeys.next();
                        if (currentArgsKey.equals("scaleArg")) {
                            if (scaleArgHash.containsKey("SCALE")) {
                                subArgs.put(scaleArgKeyHash.get("SCALE"), Math.round((scaleArgHash.get("SCALE") * l.get(i) * 0.01)));
                            }
                            if (scaleArgKeyHash.containsKey("RANDOM_SEED")) {
                                Random RANDOM_SEED = new Random();
                                subArgs.put(scaleArgKeyHash.get("RANDOM_SEED"), RANDOM_SEED.nextInt(1000000000));
                            }
                        } else {
                            if (args.get(currentArgsKey) instanceof String) {
                                subArgs.put(currentArgsKey, args.get(currentArgsKey));
                            } else if (args.get(currentArgsKey) instanceof Integer) {
                                subArgs.put(currentArgsKey, args.getInt(currentArgsKey));
                            }
                        }
                    }
                    subObj.put("args", subArgs);

                } else {
                    if (obj.get(currentKey) instanceof String) {
                        subObj.put(currentKey, obj.get(currentKey));
                    } else if (obj.get(currentKey) instanceof Integer) {
                        subObj.put(currentKey, obj.getInt(currentKey));
                    }
                }
            }
            if (obj.has("job_id")) {
                subObj.put("job_id", jobID + (i + 1));
            }
            writeJSONObjectToFile("sub-jobdescriptor" + (i + 1), subObj);

        }

    }

    public void Split_next(int X) throws JSONException, IOException {

        HashMap<String, Integer> scaleArgHash = new HashMap<String, Integer>();
        HashMap<String, String> scaleArgKeyHash = new HashMap<String, String>();
        JSONArray scaleArgArr = obj.getJSONObject("args").getJSONArray("scaleArg");
        for (int i = 0; i < scaleArgArr.length(); i++) {
            if (scaleArgArr.getJSONArray(i).get(1).equals("SCALE")) {
                scaleArgHash.put(scaleArgArr.getJSONArray(i).get(1).toString(), scaleArgArr.getJSONArray(i).getInt(2));
                scaleArgKeyHash.put("SCALE", scaleArgArr.getJSONArray(i).get(0).toString());
            } else if (scaleArgArr.getJSONArray(i).get(1).equals("RANDOM_SEED")) {
                scaleArgKeyHash.put("RANDOM_SEED", scaleArgArr.getJSONArray(i).get(0).toString());
            }
        }
        
        if (X > scaleArgHash.get("SCALE")) {
            System.err.println("Split_next(" + X + ") has been canceled.\nPlease change the argument and try again.");
            return;
        }

        JSONObject subObj = new JSONObject();

        //set job-IDs
        if (obj.has("job_id")) {
            subObj.put("job_parent_id", obj.get("job_id"));
            subObj.put("job_super_id", obj.get("job_id"));
        }

        int currentSCALE = scaleArgHash.get("SCALE");
        int newSCALE = scaleArgHash.get("SCALE");

        Iterator<String> JSON_keys = obj.keys();
        while (JSON_keys.hasNext()) {
            String currentKey = JSON_keys.next();
            if (currentKey.equals("args")) {
                JSONObject args = obj.getJSONObject("args");
                Iterator<String> argsKeys = args.keys();
                JSONObject subArgs = new JSONObject();
                while (argsKeys.hasNext()) {
                    String currentArgsKey = argsKeys.next();
                    if (currentArgsKey.equals("scaleArg")) {
                        if (scaleArgHash.containsKey("SCALE")) {
                            newSCALE = currentSCALE - X;
                            subArgs.put(scaleArgKeyHash.get("SCALE"), X);
                            this.setSCALE(newSCALE);
                        }
                        if (scaleArgKeyHash.containsKey("RANDOM_SEED")) {
                            Random RANDOM_SEED = new Random();
                            subArgs.put(scaleArgKeyHash.get("RANDOM_SEED"), RANDOM_SEED.nextInt(1000000000));
                        }
                    } else {
                        if (args.get(currentArgsKey) instanceof String) {
                            subArgs.put(currentArgsKey, args.get(currentArgsKey));
                        } else if (args.get(currentArgsKey) instanceof Integer) {
                            subArgs.put(currentArgsKey, args.getInt(currentArgsKey));
                        }
                    }
                }
                subObj.put("args", subArgs);

            } else {
                try{
                if (obj.get(currentKey) instanceof String) {
                    subObj.put(currentKey, obj.get(currentKey));
                } else if (obj.get(currentKey) instanceof Integer) {
                    subObj.put(currentKey, obj.getInt(currentKey));
                }}
                catch(org.json.JSONException j){
                    //skip
                }
            }
        }
        if (obj.has("job_id")) {
            subObj.put("job_id", jobID + (this.nextCounter));
        }
        writeJSONObjectToFile("sub-jobdescriptor" + (++this.nextCounter), subObj);
    }

    public void writeJSONObjectToFile(String filename, JSONObject obj) throws IOException, JSONException {

        FileWriter file = new FileWriter(outputFolder + "/" + filename + ".json");

        file.write(JsonWriter.formatJson(obj.toString()));

        file.flush();
        file.close();
    }
    
    private void setSCALE(int newSCALE) throws JSONException, IOException {
        JSONObject subObj = new JSONObject();

        HashMap<String, Integer> scaleArgHash = new HashMap<String, Integer>();
        HashMap<String, String> scaleArgKeyHash = new HashMap<String, String>();
        JSONArray scaleArgArr = obj.getJSONObject("args").getJSONArray("scaleArg");
        for (int i = 0; i < scaleArgArr.length(); i++) {
            if (scaleArgArr.getJSONArray(i).get(1).equals("SCALE")) {
                scaleArgHash.put(scaleArgArr.getJSONArray(i).get(1).toString(), scaleArgArr.getJSONArray(i).getInt(2));
                scaleArgKeyHash.put("SCALE", scaleArgArr.getJSONArray(i).get(0).toString());
            } else if (scaleArgArr.getJSONArray(i).get(1).equals("RANDOM_SEED")) {
                scaleArgKeyHash.put("RANDOM_SEED", scaleArgArr.getJSONArray(i).get(0).toString());
            }
        }

        Iterator<String> JSON_keys = obj.keys();
        while (JSON_keys.hasNext()) {
            String currentKey = JSON_keys.next();
            if (currentKey.equals("args")) {
                JSONObject args = obj.getJSONObject("args");
                Iterator<String> argsKeys = args.keys();
                JSONObject subArgs = new JSONObject();
                while (argsKeys.hasNext()) {
                    String currentArgsKey = argsKeys.next();
                    if (currentArgsKey.equals("scaleArg")) {
                        if (scaleArgHash.containsKey("SCALE")) {
                            subArgs.put(scaleArgKeyHash.get("SCALE"), newSCALE);
                        }
                        if (scaleArgKeyHash.containsKey("RANDOM_SEED")) {
                            Random RANDOM_SEED = new Random();
                            subArgs.put(scaleArgKeyHash.get("RANDOM_SEED"), RANDOM_SEED.nextInt(1000000000));
                        }
                    } else {
                        if (args.get(currentArgsKey) instanceof String) {
                            subArgs.put(currentArgsKey, args.get(currentArgsKey));
                        } else if (args.get(currentArgsKey) instanceof Integer) {
                            subArgs.put(currentArgsKey, args.getInt(currentArgsKey));
                        }
                    }
                }
                subObj.put("args", subArgs);

            } else {
                if (obj.get(currentKey) instanceof String) {
                    subObj.put(currentKey, obj.get(currentKey));
                } else if (obj.get(currentKey) instanceof Integer) {
                    subObj.put(currentKey, obj.getInt(currentKey));
                }
            }
        }
        obj = subObj;

        writeJSONObjectToFile("jobdescriptor" + (++this.currentJobDescriptor), subObj);
    }
   
    public static ArrayList<String> getInputFiles(){
        ArrayList<String> jds = new ArrayList<String>();
        
        File path = new File("input/");

        File [] files = path.listFiles();
        for (int i = 0; i < files.length; i++){
            if (files[i].isFile()){
                jds.add(files[i].toString());
            }
        }
        return jds;
    }

    public static void main(String[] args) throws IOException, JSONException, InterruptedException, IllegalArgumentException, IllegalAccessException, NoSuchFieldException, SecurityException, UnknownHostException {

        initArgs();

        initDir(new File("output"));
        for(String arg : args){
            JobDescriptor jd = new JobDescriptor(arg);
            jd.Split_equal();
        }
        
    }
}

