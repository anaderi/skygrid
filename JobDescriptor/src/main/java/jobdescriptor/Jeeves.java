package jobdescriptor;

import java.io.IOException;

/**
 *
 * @author Dimitris Sarigiannis
 */
public class Jeeves {

	private JobDescriptor jd;
	
	public Jeeves(JobDescriptor jd)throws IOException, InterruptedException, IllegalArgumentException, IllegalAccessException, NoSuchFieldException, SecurityException{
		System.out.println("Jeeves has been started...");
		
		this.jd = jd;
		
		String home = System.getProperty("user.home");
		
		executeFairShip(home);
		writeFilesToHDFS(home);
	}
	
	private static void executeFairShip(String home) throws IllegalArgumentException, IllegalAccessException, NoSuchFieldException, SecurityException, InterruptedException, IOException{
		//assuming that FairShip project is located in user's home folder
		CommandExecutor.execute(home+"/FairShip","./vm/start.sh");
		CommandExecutor.execute(home+"/FairShip","./vm/build_ship.sh");
		CommandExecutor.execute(home+"/FairShip","./vm/run.sh 'cd /opt/ship/build; . ./config.sh; macro/run_simScript.py'");
		//return status (try-catch)
	}
	
	private static void writeFilesToHDFS(String home) throws IllegalArgumentException, IllegalAccessException, NoSuchFieldException, SecurityException, InterruptedException, IOException{
		//write to hdfs
		System.out.println("\nCreating directory to hdfs...");
		CommandExecutor.execute(home+"/FairShip","sudo -u hdfs hadoop fs -mkdir /user/jeeves/");
		CommandExecutor.execute(home+"/FairShip","sudo -u hdfs hadoop fs -mkdir /user/jeeves/machine/");
		CommandExecutor.execute(home+"/FairShip","sudo -u hdfs hadoop fs -mkdir /user/jeeves/machine/runid/");
		System.out.println("Copying files to tmp directory...");
		CommandExecutor.execute(home+"/FairShip","cp "+home+"/FairShip/"+"build/ship.Pythia8-TGeant4.root /tmp/");
		System.out.println("Writing files to hdfs...");
		CommandExecutor.execute(home+"/FairShip","sudo -u hdfs hadoop fs -copyFromLocal " +"/tmp/ship.Pythia8-TGeant4.root /user/jeeves/machine/runid/");
		System.out.println("Printing...");
		CommandExecutor.execute(home+"/FairShip","sudo -u hdfs hadoop fs -ls /user/jeeves/machine/runid/");
		System.out.println("Jeeves has been terminated...");
		//return status (try-catch)
	}

}
