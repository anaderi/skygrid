package jobdescriptor;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

public class CommandExecutor {

    public static String execute(String absolutePath,String command) throws InterruptedException{
        StringBuilder sb = new StringBuilder();
	String[] commands = new String[]{"/bin/bash","-c", command};
        try {
            Process proc = buildProcess(absolutePath,commands).start();
	    
	    BufferedReader stdInput = new BufferedReader(new InputStreamReader(proc.getInputStream()));

            BufferedReader stdError = new BufferedReader(new InputStreamReader(proc.getErrorStream()));

            String s = null;

            while ((s = stdInput.readLine()) != null) {
		System.out.println(s);
                sb.append(s);
                sb.append("\n");
            }

            while ((s = stdError.readLine()) != null) {
		System.out.println(s);                
		sb.append(s);
                sb.append("\n");
            }

	} catch (IOException e) {
            e.printStackTrace();
        }
        return sb.toString();
    }

    public static ProcessBuilder buildProcess(String absolutePath, String[] commands) throws IOException {
        ProcessBuilder pb = new ProcessBuilder(commands);
        return pb.directory(new File(absolutePath));
    }

}
