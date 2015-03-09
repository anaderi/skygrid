package com.github.anaderi.skygrid.executor.common;

import org.apache.hadoop.yarn.api.ApplicationConstants;
import org.apache.hadoop.yarn.api.protocolrecords.GetNewApplicationResponse;
import org.apache.hadoop.yarn.api.records.*;
import org.apache.hadoop.yarn.client.api.YarnClient;
import org.apache.hadoop.yarn.client.api.YarnClientApplication;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.apache.hadoop.yarn.util.Records;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.util.*;

/**
 * This is a helper class for execution Applications masters,
 * according to a pattern.
 */
public class ApplicationMasterExecutor {

    public ApplicationMasterExecutor(String classToExecute, String appName) throws YarnException, IOException {
        classToExecute_ = classToExecute;
        appName_ = appName;
        conf_ = new YarnConfiguration();
        yarnClient_ = YarnClient.createYarnClient();
        yarnClient_.init(conf_);
        yarnClient_.start();
    }

    public ApplicationId getApplicationId() throws IOException, YarnException {
        applicationClient_ = yarnClient_.createApplication();
        GetNewApplicationResponse newApplicationResponse = applicationClient_.getNewApplicationResponse();
        ApplicationId applicationId = newApplicationResponse.getApplicationId();
        LOG.debug("We were granted to start an application. Id = %s", applicationId);
        return applicationId;
    }

    public void submitApplication(URL destJarPath,
                                  long destJarLength,
                                  long destJarModificationTime,
                                  List<String> extraArguments) throws IOException, YarnException {

        destJarPath_ = destJarPath;
        destJarLength_ = destJarLength;
        destJarModificationTime_ = destJarModificationTime;
        extraArguments_ = extraArguments;

        ApplicationSubmissionContext applicationContext = applicationClient_.getApplicationSubmissionContext();
        applicationContext.setApplicationName(appName_);
        applicationContext.setAMContainerSpec(getApplicationsContainerLaunchContext());
        applicationContext.setResource(getApplicationRequiredResources());
        yarnClient_.submitApplication(applicationContext);
    }

    public void startApplication(URL destJarPath,
                                 long destJarLength,
                                 long destJarModificationTime,
                                 List<String> extraArguments) throws IOException, YarnException {
        getApplicationId();
        submitApplication(destJarPath, destJarLength, destJarModificationTime, extraArguments);
    }

    private ContainerLaunchContext getApplicationsContainerLaunchContext() throws IOException {
        ContainerLaunchContext amContainer = Records.newRecord(ContainerLaunchContext.class);
        amContainer.setLocalResources(getApplicationsResources());
        amContainer.setEnvironment(getApplicationsEnvironment());
        amContainer.setCommands(getApplicationsCommands());
        return amContainer;
    }

    private Resource getApplicationRequiredResources() {
        Resource capability = Records.newRecord(Resource.class);
        capability.setMemory(512);
        return capability;
    }

    private Map<String, LocalResource> getApplicationsResources() throws IOException {
        LocalResource jarResource = Records.newRecord(LocalResource.class);
        jarResource.setResource(destJarPath_);
        jarResource.setSize(destJarLength_);
        jarResource.setTimestamp(destJarModificationTime_);
        jarResource.setType(LocalResourceType.FILE);
        jarResource.setVisibility(LocalResourceVisibility.APPLICATION);
        Map<String, LocalResource> localResources = new HashMap<String, LocalResource>();
        localResources.put(APP_JAR_NAME, jarResource);
        return localResources;
    }

    private String getApplicationsClasspath() {
        StringBuilder classPathEnv = new StringBuilder().append(File.pathSeparatorChar).append("./" + APP_JAR_NAME);
        for (String c : conf_.getStrings(YarnConfiguration.YARN_APPLICATION_CLASSPATH,
                YarnConfiguration.DEFAULT_YARN_APPLICATION_CLASSPATH)) {
            classPathEnv.append(File.pathSeparatorChar);
            classPathEnv.append(c.trim());
        }
        classPathEnv.append(File.pathSeparatorChar);
        classPathEnv.append(ApplicationConstants.Environment.CLASSPATH.$());
        return classPathEnv.toString();
    }

    private Map<String, String> getApplicationsEnvironment() {
        Map<String, String> env = new HashMap<String, String>();
        env.put("AMJAR", destJarPath_.toString());
        env.put("AMJARTIMESTAMP", Long.toString(destJarModificationTime_));
        env.put("AMJARLEN", Long.toString(destJarLength_));
        env.put("CLASSPATH", getApplicationsClasspath());
        env.put("_JAVA_OPTIONS", "-Djava.net.preferIPv4Stack=false");
        return env;
    }


    private List<String> getApplicationsCommands() {
        Vector<CharSequence> vargs = new Vector<CharSequence>(30);
        vargs.add(ApplicationConstants.Environment.JAVA_HOME.$() + "/bin/java");
        vargs.add(classToExecute_);
        if (extraArguments_ != null) {
            vargs.addAll(extraArguments_);
        }
        vargs.add("1><LOG_DIR>/AM.stdout");
        vargs.add("2><LOG_DIR>/AM.stderr");
        StringBuilder command = new StringBuilder();
        for (CharSequence str : vargs) {
            command.append(str).append(" ");
        }
        List<String> commands = new ArrayList<String>();
        commands.add(command.toString());
        return commands;
    }

    private static final Logger LOG = LoggerFactory.getLogger(ApplicationMasterExecutor.class);
    public static final String APP_JAR_NAME = "app.jar";
    private final YarnConfiguration conf_;
    private final YarnClient yarnClient_;
    private YarnClientApplication applicationClient_;
    private final String appName_;
    private final String classToExecute_;
    private URL destJarPath_;
    private long destJarLength_;
    private long destJarModificationTime_;
    private List<String> extraArguments_;
}
