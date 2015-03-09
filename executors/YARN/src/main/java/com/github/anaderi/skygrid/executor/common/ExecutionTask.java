package com.github.anaderi.skygrid.executor.common;


import java.util.List;
import java.util.Map;

public class ExecutionTask {
    public AppContainer app_container;
    public Map<String, String> args;
    public String cmd;
    public Integer cpu_per_container;
    public String email;
    public EnvContainer env_container;
    public Integer job_id;
    public Integer job_parent_id;
    public Integer job_super_id;
    public Integer max_memoryMB;
    public Integer min_memoryMB;
    public String name;
    public Integer num_containers;
    public String status;

    public static class AppContainer {
        public String name;
        public String volume;
    }

    public static class EnvContainer {
        public String app_volume;
        public String name;
        public String output_volume;
        public String workdir;
    }
}
