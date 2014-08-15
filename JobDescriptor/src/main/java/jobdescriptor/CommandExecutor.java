package jobdescriptor;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.util.Scanner;

public class CommandExecutor {

	public synchronized static String execute(String absolutePath, String command)
			throws InterruptedException, IOException, IllegalArgumentException, IllegalAccessException, NoSuchFieldException, SecurityException {
		StringBuilder sb = new StringBuilder();
		String[] commands = new String[] { "/bin/bash", "-c", command };
		
		Process proc = null;
		String sem = "semaphore";
		ProcessBuilder pb = null;
		
		synchronized (sem) {
			try {
				BufferedReader stdInput = null;
				BufferedReader stdError = null;
				pb = buildProcess(absolutePath, commands);
				proc = pb.start();

				stdInput = new BufferedReader(new InputStreamReader(
						proc.getInputStream()));
				//System.out.println(proc.getInputStream());

				stdError = new BufferedReader(new InputStreamReader(
						proc.getErrorStream()));
				
				String s = null;
				

				int i = 0;
				
				Scanner scanner = new Scanner(proc.getInputStream());
				
				while (scanner.hasNext() && ((s = scanner.nextLine()) != null)) {
					sb.append(s);
					sb.append("\n");
					if (i == 1373 || i == 116) {
						//System.out.println("STOP");
						if (!stdInput.ready()) {
							break;
						}
					}
					System.out.println(s);
					i++;
					//System.out.println(i);

				}

				while (stdError.ready() && ((s = stdError.readLine()) != null)) {
					sb.append(s);
					sb.append("\n");
				}

				stdInput.close();
				stdError.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
			
			return sb.toString();
		}
		
	}

	public static ProcessBuilder buildProcess(String absolutePath,
			String[] commands) throws IOException {
		ProcessBuilder pb = new ProcessBuilder(commands);
		return pb.directory(new File(absolutePath));
	}

}

