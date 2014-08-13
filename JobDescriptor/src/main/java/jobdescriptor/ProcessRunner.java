package jobdescriptor;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.File;

    class ProcessRunner extends Thread {

        ProcessBuilder b;
        Process p;
        boolean done = false;

        ProcessRunner(String[] args) {
            super("ProcessRunner " + args);
            b = new ProcessBuilder(args);
	    b.directory(new File(System.getProperty("user.home")+"/FairShip"));
        }

        @Override
        public void run() {
            StringBuilder sb = new StringBuilder();
            try {
                p = b.start();
                
                // Do your buffered reader and readline stuff here
                BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));
                BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));
                String s = null;
                while ((s = stdInput.readLine()) != null) {
                    sb.append(s);
                    sb.append("\n");
                }

                while ((s = stdError.readLine()) != null) {
                    sb.append(s);
                    sb.append("\n");
                }
                System.out.println(sb);
                
                // wait for the process to complete
                p.waitFor();
            } catch (Exception e) {
                System.err.println(e.getMessage());
            } finally {
                // some cleanup code
                done = true;
            }
        }

        int exitValue() throws IllegalStateException {
            if (p != null) {
                return p.exitValue();
            }
            throw new IllegalStateException("Process not started yet");
        }

        boolean isDone() {
            return done;
        }

        void abort() {
            if (!isDone()) {
                // do some cleanup first
                p.destroy();
            }
        }
    }
