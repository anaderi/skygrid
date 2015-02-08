package com.github.anaderi.skygrid.executor.jeeves;

import com.github.anaderi.skygrid.executor.common.ExecutionTask;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.Date;

/**
 * Created by stromsund on 25/01/15.
 */
public class Jeeves {

    public static void main(String[] args) throws InterruptedException, IOException {
        System.out.println("Hello, world!");
        try {
            String task = URLDecoder.decode(args[0], "UTF-8");
            String url_to_put_result = args[1];

            ObjectMapper mapper = new ObjectMapper();
            mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
            ExecutionTask executionTask = mapper.readValue(task, ExecutionTask.class);

            long time_before_pull = (new Date()).getTime();

            ProcessBuilder processBuilder = new ProcessBuilder("sudo", "/usr/bin/docker", "pull", executionTask.getApp());
            processBuilder.redirectErrorStream(true);
            Process proc = processBuilder.start();
            BufferedReader is = new BufferedReader(new InputStreamReader(proc.getInputStream()));

            FileSystem fileSystem = FileSystem.get(new YarnConfiguration());
            Path p = new Path(url_to_put_result);
            FSDataOutputStream file = fileSystem.create(p);
            String line;
            while ((line = is.readLine()) != null) {
                file.writeChars("Pull Output: ");
                file.writeChars(line);
                file.writeChars("\n");
            }
            //file.writeChars(task);
            //file.flush();
            proc.waitFor();
            long time_after_pull = (new Date()).getTime();
            file.writeChars(String.format("Pull taken %d seconds\n", time_after_pull - time_before_pull));
            file.writeChars("Executing container...");
            if (0 != proc.exitValue()) {
                file.writeChars("Pull was not successful.");
                file.close();
                return;
            }

            processBuilder = new ProcessBuilder("sudo", "/usr/bin/docker", "run", executionTask.getApp(), executionTask.getCmd());
            processBuilder.redirectErrorStream(true);
            proc = processBuilder.start();
            is = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            while ((line = is.readLine()) != null) {
                file.writeChars("Docker Output: ");
                file.writeChars(line);
                file.writeChars("\n");
            }
            file.close();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        System.out.flush();
        Thread.sleep(60000);
    }
}
