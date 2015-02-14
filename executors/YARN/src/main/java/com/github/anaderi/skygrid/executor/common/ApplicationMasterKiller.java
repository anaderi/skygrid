package com.github.anaderi.skygrid.executor.common;

import org.apache.hadoop.yarn.api.records.ApplicationId;
import org.apache.hadoop.yarn.client.api.YarnClient;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;

import java.io.IOException;

public class ApplicationMasterKiller {
    public ApplicationMasterKiller(String appId) throws YarnException, IOException {
        String[] tokens = appId.split("_");
        YarnConfiguration conf = new YarnConfiguration();
        YarnClient yarnClient = YarnClient.createYarnClient();
        yarnClient.init(conf);
        yarnClient.start();
        long timestamp = Long.valueOf(tokens[1], 10);
        int id = Integer.valueOf(tokens[2], 10);
        yarnClient.killApplication(ApplicationId.newInstance(timestamp, id));
        System.out.printf("Application %s %s is killed\n", timestamp, id);
    }
}
