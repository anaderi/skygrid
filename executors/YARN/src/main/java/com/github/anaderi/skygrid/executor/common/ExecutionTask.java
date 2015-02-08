package com.github.anaderi.skygrid.executor.common;


import java.util.List;

public class ExecutionTask {
    public String getApp() {
        return app;
    }

    public void setApp(String app) {
        this.app = app;
    }

    public List<String> getEnvironments() {
        return environments;
    }

    public void setEnvironments(List<String> environment) {
        this.environments = environment;
    }

    public String getCmd() {
        return cmd;
    }

    public void setCmd(String cmd) {
        this.cmd = cmd;
    }

    private String app;
    private String cmd;
    private List<String> environments;
}
