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
		
		//assuming that FairShip project is located in user's home folder
		CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/start.sh");
		CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/build_ship.sh");
		CommandExecutor.execute(System.getProperty("user.home")+"/FairShip","./vm/run.sh 'cd /opt/ship/build; . ./config.sh; macro/run_simScript.py'");

		System.out.println("Jeeves has been terminated...");
	}

}

