package jeeves;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.sql.Time;

import org.json.JSONException;

import jobdescriptor.JobDescriptor;

/**
 * 
 * @author Dimitris Sarigiannis
 */
public class Jeeves {

	private JobDescriptor jd;
	private String FairShipLocation;
	private String machine;
	private String currentTime;
	private String resultsFilename;

	/*
	 * 0 <-- jeeves has terminated normaly 
	 * 1 <-- jeeves has not started yet
	 * 2 <-- jeeves has terminated with errors
	 */
	private int jeevesStatus;

	public Jeeves(JobDescriptor jd) throws IOException, InterruptedException,
			IllegalArgumentException, IllegalAccessException,
			NoSuchFieldException, SecurityException, UnknownHostException {
		System.out.println("Jeeves has been started...");

		jeevesStatus = 1;

		machine = InetAddress.getLocalHost().getHostName();
		currentTime = new Time(System.currentTimeMillis()).toString().replace(
				":", "");
		// assuming that FairShip project is located in user's home folder
		FairShipLocation = System.getProperty("user.home");
		resultsFilename = "ship.Pythia8-TGeant4.root";

		this.jd = jd;

		executeFairShip();

		System.out.println("Jeeves has been terminated...");
	}

	private void executeFairShip() throws IllegalArgumentException,
			IllegalAccessException, NoSuchFieldException, SecurityException,
			InterruptedException, IOException {

		try {
			CommandExecutor.execute(FairShipLocation + "/FairShip",
					"./vm/start.sh");
			CommandExecutor.execute(FairShipLocation + "/FairShip",
					"./vm/build_ship.sh");
			CommandExecutor
					.execute(FairShipLocation + "/FairShip",
							"./vm/run.sh 'cd /opt/ship/build; . ./config.sh; macro/run_simScript.py'");
			jeevesStatus = 0;
		} catch (Exception e) {
			jeevesStatus = 2;
		}
	}

	/*
	 * write Jeeves results to HDFS
	 */
	public void writeFairShipResultsToHDFS() throws IllegalArgumentException,
			IllegalAccessException, NoSuchFieldException, SecurityException,
			InterruptedException, IOException, UnknownHostException {
		// write to hdfs
		System.out.println("\nCreating directory to hdfs...");
		CommandExecutor.execute(FairShipLocation + "/FairShip",
				"sudo -u hdfs hadoop fs -mkdir -p /user/jeeves/" + machine
						+ "/" + currentTime + "/");

		System.out.println("Copying files to tmp directory...");
		writeFairShipResultsToLocal("/tmp/");

		System.out.println("Writing files to hdfs...");
		CommandExecutor.execute(FairShipLocation + "/FairShip",
				"sudo -u hdfs hadoop fs -copyFromLocal " + "/tmp/" + resultsFilename
						+ " /user/jeeves/" + machine + "/" + currentTime + "/");

		System.out.println("Printing...");
		CommandExecutor.execute(FairShipLocation + "/FairShip",
				"sudo -u hdfs hadoop fs -ls /user/jeeves/" + machine + "/");
		// return status (try-catch)
	}

	/*
	 * write Jeeves results localy
	 */
	public void writeFairShipResultsToLocal(String localPath)
			throws InterruptedException, IOException, IllegalAccessException,
			NoSuchFieldException {
		CommandExecutor.execute(FairShipLocation + "/FairShip", "cp "
				+ FairShipLocation + "/FairShip/" + "build/" + resultsFilename + " "
				+ localPath);
	}

	/*
	 * returns status of Jeeves
	 */
	public int getjeevesStatus() {
		return jeevesStatus;
	}

	/**
	 * @param args
	 *            the command line arguments
	 * @throws InterruptedException
	 * @throws SecurityException
	 * @throws NoSuchFieldException
	 * @throws IllegalAccessException
	 * @throws IllegalArgumentException
	 */
	public static void main(String[] args) throws IOException, JSONException,
			InterruptedException, IllegalArgumentException,
			IllegalAccessException, NoSuchFieldException, SecurityException,
			UnknownHostException {
		// TODO
		JobDescriptor jd = new JobDescriptor("jobdescriptor");

		Jeeves jeeves = new Jeeves(jd);
		if (jeeves.getjeevesStatus() == 0) {
			jeeves.writeFairShipResultsToHDFS();
		}

	}

}
