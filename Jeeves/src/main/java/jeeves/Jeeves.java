package jeeves;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.sql.Time;

import org.json.JSONException;

import jobdescriptor.JobDescriptor;

import java.io.IOException;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;

import java.util.Properties;

import net.schmizz.sshj.SSHClient;

import org.apache.commons.io.IOUtils;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClientBuilder;

import com.jcraft.jsch.Channel;
import com.jcraft.jsch.ChannelExec;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.Session;

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

	// HTTP POST request
	private void sendPost() throws Exception {

		//unknown url at the moment
		String url = "http://...";

		HttpClient httpclient = HttpClientBuilder.create().build();
		HttpPost post = new HttpPost(url);

		// add header
		//post.setHeader("Content-Type", "application/root");
		try {
			post.setEntity(new StringEntity(
					getContentOfFile(FairShipLocation + "/FairShip/" + "build/" + resultsFilename)));

			HttpResponse response = httpclient.execute(post);
			System.out.println("\nSending 'POST' request to URL : " + url);
			System.out.println("Post parameters : " + post.getEntity());
			System.out.println("Response Code : "
					+ response.getStatusLine().getStatusCode());
			
			/* //print
			BufferedReader rd = new BufferedReader(new InputStreamReader(
					response.getEntity().getContent()));

			StringBuffer result = new StringBuffer();
			String line = "";
			while ((line = rd.readLine()) != null) {
				result.append(line);
			}*/
			
			
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

	}

	private String getContentOfFile(String filename) throws IOException {
		FileInputStream inputStream = new FileInputStream(filename);
		try {
			String str = IOUtils.toString(inputStream);
			return str;
		} finally {
			inputStream.close();
		}
	}

	private void sendWithSCP() {
		System.out.println("SCP START");

		FileInputStream fis = null;
		try {

			String lfile = "FairRunInfo_ship.Pythia8-TGeant4.root";
			String user = "username";

			String host = "127.0.0.1";
			String rfile = "test.txt";

			JSch jsch = new JSch();
			Session session = jsch.getSession(user, host, 22);
			session.setPassword("********");

			Properties config = new Properties();
			config.put("StrictHostKeyChecking", "no");
			session.setConfig(config);
			session.connect();

			boolean ptimestamp = true;

			// exec 'scp -t rfile' remotely
			String command = "scp " + (ptimestamp ? "-p" : "") + " -t " + rfile;
			Channel channel = session.openChannel("exec");
			((ChannelExec) channel).setCommand(command);

			// get I/O streams for remote scp
			OutputStream out = channel.getOutputStream();
			InputStream in = channel.getInputStream();

			channel.connect();

			if (checkAck(in) != 0) {
				System.exit(0);
			}

			File _lfile = new File(lfile);

			if (ptimestamp) {
				command = "T " + (_lfile.lastModified() / 1000) + " 0";
				// The access time should be sent here,
				// but it is not accessible with JavaAPI ;-<
				command += (" " + (_lfile.lastModified() / 1000) + " 0\n");
				out.write(command.getBytes());
				out.flush();
				if (checkAck(in) != 0) {
					System.exit(0);
				}
			}

			// send "C0644 filesize filename", where filename should not include
			// '/'
			long filesize = _lfile.length();
			command = "C0644 " + filesize + " ";
			if (lfile.lastIndexOf('/') > 0) {
				command += lfile.substring(lfile.lastIndexOf('/') + 1);
			} else {
				command += lfile;
			}
			command += "\n";
			out.write(command.getBytes());
			out.flush();
			if (checkAck(in) != 0) {
				System.exit(0);
			}

			// send a content of lfile
			fis = new FileInputStream(lfile);
			byte[] buf = new byte[1024];
			while (true) {
				int len = fis.read(buf, 0, buf.length);
				if (len <= 0)
					break;
				out.write(buf, 0, len); // out.flush();
			}
			fis.close();
			fis = null;
			// send '\0'
			buf[0] = 0;
			out.write(buf, 0, 1);
			out.flush();
			if (checkAck(in) != 0) {
				System.exit(0);
			}
			out.close();

			channel.disconnect();
			session.disconnect();
			System.out.println("SCP END");
			System.exit(0);
		} catch (Exception e) {
			System.out.println(e);
			try {
				if (fis != null)
					fis.close();
			} catch (Exception ee) {
			}
		}
	}

	private int checkAck(InputStream in) throws IOException {
		int b = in.read();
		// b may be 0 for success,
		// 1 for error,
		// 2 for fatal error,
		// -1
		if (b == 0)
			return b;
		if (b == -1)
			return b;

		if (b == 1 || b == 2) {
			StringBuffer sb = new StringBuffer();
			int c;
			do {
				c = in.read();
				sb.append((char) c);
			} while (c != '\n');
			if (b == 1) { // error
				System.out.print(sb.toString());
			}
			if (b == 2) { // fatal error
				System.out.print(sb.toString());
			}
		}
		return b;
	}

}
