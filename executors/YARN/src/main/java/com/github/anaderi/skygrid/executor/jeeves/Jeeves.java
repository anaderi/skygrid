package com.github.anaderi.skygrid.executor.jeeves;

import com.github.anaderi.skygrid.executor.common.ExecutionTask;
import com.github.anaderi.skygrid.executor.common.JobDescriptor;
import com.sun.tools.javac.util.Convert;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.lang.reflect.Array;
import java.net.URLDecoder;
import java.util.*;


public class Jeeves {
    private static final Logger LOG = LoggerFactory.getLogger(Jeeves.class);
    private static final String DOCKER = "/usr/bin/docker";

    public static void main(String[] args) {
        String app_container_id = null;
        String app_container_name;
        String env_container_id = null;
        try {
            String task = URLDecoder.decode(args[0], "UTF-8");
            String url_to_put_result = args[1];

            ObjectMapper mapper = new ObjectMapper();
            mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
            JobDescriptor executionTask = mapper.readValue(task, JobDescriptor.class);
            System.out.println("Execution task received");

            // At first we need to pull application and environment containers.
            pullImage(executionTask.job.descriptor.app_container.name);
            pullImage(executionTask.job.descriptor.env_container.name);

            // Start app container
            app_container_name = String.format("APP_CONTAINER_FOR_%s", executionTask.job.job_id);
            app_container_id = startAppContainer(executionTask, app_container_name);

            // Start env container
            env_container_id = startEnvContainer(executionTask, app_container_name);

            while (isContainerStillRunning(env_container_id))
                Thread.sleep(5000);
            /*
            ProcessBuilder processBuilder = new ProcessBuilder("sudo", "/usr/bin/docker", "pull", executionTask.cmd);
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

            processBuilder = new ProcessBuilder("sudo", "/usr/bin/docker", "run", executionTask.cmd, executionTask.cmd);
            processBuilder.redirectErrorStream(true);
            proc = processBuilder.start();
            is = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            while ((line = is.readLine()) != null) {
                file.writeChars("Docker Output: ");
                file.writeChars(line);
                file.writeChars("\n");
            }
            file.close();
            */
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if (app_container_id != null) {
                    removeContainer(app_container_id, true);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        System.out.flush();
        try {
            Thread.sleep(60000);
        } catch (InterruptedException e) {}
    }

    private static void pullImage(String image_name) throws IOException, InterruptedException {
        LOG.info("Downloading image {}", image_name);
        long time_before_pull = (new Date()).getTime();
        ProcessBuilder processBuilder = new ProcessBuilder("sudo", DOCKER, "pull", image_name);
        processBuilder.redirectErrorStream(true);
        Process proc = processBuilder.start();
        BufferedReader is = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        String line;
        while ((line = is.readLine()) != null) {
            LOG.info(line);
        }
        proc.waitFor();
        long time_after_pull = (new Date()).getTime();
        LOG.info("Pull completed in {} seconds", (time_after_pull - time_before_pull));
        if (0 != proc.exitValue()) {
            LOG.error("An error occurred while downloading image {}", image_name);
            throw new IOException();
        }
    }

    private static String startContainer(List<String> command) throws IOException, InterruptedException {
        LOG.info("Starting container {}", command);
        ProcessBuilder processBuilder = new ProcessBuilder(command);
        processBuilder.redirectErrorStream(true);
        Process proc = processBuilder.start();
        BufferedReader is = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        String first_line = is.readLine();
        if (is.ready()) {
            // In case of successful execution first_line contains container_ID.
            // But in case of errors it contains error message.
            LOG.error(first_line);
            // Read all lines, in case of errors.
            String line;
            while ((line = is.readLine()) != null) {
                LOG.error(line);
            }
        }
        proc.waitFor();
        if (0 != proc.exitValue()) {
            LOG.error("An error occurred while starting container");
            throw new IOException();
        }
        return first_line;
    }

    private static String startAppContainer(JobDescriptor descriptor,
                                            String name) throws IOException, InterruptedException {
        LOG.info("Starting app container {}", descriptor.job.descriptor.app_container.name);
        String[] command = {
            "sudo", DOCKER, "run", "-d",
            "-v", descriptor.job.descriptor.app_container.volume,
            "--name", name,
            descriptor.job.descriptor.app_container.name};
        return startContainer(Arrays.asList(command));
    }

    private static String startEnvContainer(JobDescriptor descriptor,
                                            String app_container_name) throws IOException, InterruptedException {
        LOG.info("Starting env container {}", descriptor.job.descriptor.env_container.name);
        File hostOutputDir = new File("/tmp/" + app_container_name);
        hostOutputDir.mkdir();

        Map<String, String> substitutions = new HashMap<String, String>(3);
        substitutions.put("$DATA_DIR", "/data");
        substitutions.put("$OUTPUT_DIR", "/output");
        substitutions.put("$JOB_ID", descriptor.job.descriptor.job_id.toString());

        String[] command = {
            "sudo", DOCKER, "run", "-d",
            "--volumes-from", app_container_name,
            "-v", String.format("%s:/output", hostOutputDir.toString()),
            "-w", descriptor.job.descriptor.env_container.workdir,
            descriptor.job.descriptor.env_container.name,
            descriptor.job.descriptor.cmd + generateArguments(descriptor.job.descriptor.args, substitutions)
        };
        return startContainer(Arrays.asList(command));
    }

    private static void removeContainer(String container_id,
                                        boolean with_volumes) throws IOException, InterruptedException {
        LOG.info("Removing container {}", container_id);
        ProcessBuilder processBuilder;
        if (with_volumes) {
            processBuilder = new ProcessBuilder("sudo", DOCKER, "rm", "--force", "--volumes", container_id);
        } else {
            processBuilder = new ProcessBuilder("sudo", DOCKER, "rm", "--force", container_id);
        }
        processBuilder.redirectErrorStream(true);
        Process proc = processBuilder.start();
        BufferedReader is = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        String line;
        while ((line = is.readLine()) != null) {
            LOG.info(line);
        }
        proc.waitFor();
        LOG.info("Removing container {} is complete", container_id);
    }

    public static String generateArguments(Map<String, String> job_arguments,
                                           Map<String, String> substitution) {
        List<String> pos_arguments = new ArrayList<String>();
        List<String> kw_arguments = new ArrayList<String>();
        for (Map.Entry<String, String> item : job_arguments.entrySet()) {
            String value = item.getValue();
            for (Map.Entry<String, String> substitution_item : substitution.entrySet()) {
                value = value.replace(substitution_item.getKey(), substitution_item.getValue());
            }
            if (item.getKey().startsWith("__POS")) {
                pos_arguments.add(value);
            } else {
                kw_arguments.add(String.format("%s=%s", item.getKey(), value));
            }
        }
        StringBuilder arguments_builder = new StringBuilder();
        for (String arg : pos_arguments) {
            arguments_builder.append(' ');
            arguments_builder.append(arg);
        }
        for (String arg : kw_arguments) {
            arguments_builder.append(' ');
            arguments_builder.append(arg);
        }
        return arguments_builder.toString();
    }

    public static boolean isContainerStillRunning(String container_id) throws IOException, InterruptedException {
        LOG.info("Checking, if container {} still running", container_id);
        ProcessBuilder processBuilder = new ProcessBuilder("sudo", DOCKER, "ps", "-q", "--no-trunc=true");
        processBuilder.redirectErrorStream(true);
        Process proc = processBuilder.start();
        BufferedReader is = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        String line;
        boolean result = false;
        while ((line = is.readLine()) != null) {
            if (line.equals(container_id))
                result = true;
        }
        proc.waitFor();
        LOG.info("{} is running = {}", container_id, result);
        return result;
    }
}
