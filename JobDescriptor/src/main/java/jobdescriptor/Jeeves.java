package jobdescriptor;

import com.cedarsoftware.util.io.JsonWriter;
import java.lang.ProcessBuilder;
import java.io.File;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Random;
import java.util.Map;
import java.util.HashMap;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 *
 * @author Dimitris Sarigiannis
 */
public class Jeeves {

	private JobDescriptor jd;
	
	public Jeeves(JobDescriptor jd)throws IOException, InterruptedException{
		System.out.println("Jeeves start...");
		
		this.jd = jd;
		
		//assuming that FairShip project is located in home folder
		System.out.println( CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/start.sh") );
		System.out.println( CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/build_ship.sh") );
		//System.out.println( CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/run.sh 'cd /opt/ship/build; . ./config.sh; macro/run_simScript.py'") );
		
		//System.out.println( CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/run.sh bash") );
/*
		String[] a = {"./vm/start.sh"};
		ProcessRunner pr = new ProcessRunner(a);
		pr.start();
		// wait for 100ms
		pr.join(6000);
		// process still going on? kill it!
		if(!pr.isDone()){
			System.out.println("Destroying process " + pr);
			pr.abort();		
		}
*/		
		System.out.println("Jeeves terminated...");
	}

}
