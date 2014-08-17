package ru.yandex.cern.yarntest;

import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.api.ApplicationConstants;
import org.apache.hadoop.yarn.api.protocolrecords.GetNewApplicationResponse;
import org.apache.hadoop.yarn.api.protocolrecords.RegisterApplicationMasterResponse;
import org.apache.hadoop.yarn.api.records.*;
import org.apache.hadoop.yarn.api.records.URL;
import org.apache.hadoop.yarn.client.api.AMRMClient;
import org.apache.hadoop.yarn.client.api.YarnClient;
import org.apache.hadoop.yarn.client.api.YarnClientApplication;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.apache.hadoop.yarn.util.ConverterUtils;
import org.apache.hadoop.yarn.util.Records;
import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.*;
import java.util.*;


public class SeniorApplicationMaster {

    private static final Logger LOG =
            LoggerFactory.getLogger(ApplicationMaster.class);
    private YarnConfiguration yarnConfiguration = new YarnConfiguration();
    private SeniorApplicationMasterProperties seniorApplicationMasterProperties;
    private AMRMClientAsync<AMRMClient.ContainerRequest> amRMClient;
    private YarnClient yarnClient;
    private XmlRpcClientConfigImpl metaSchedulerConfig = new XmlRpcClientConfigImpl();
    private XmlRpcClient client;
    private long jeeves_task_id = 0;
    private FileSystem fileSystem;

    public SeniorApplicationMaster(String auntAgathaURL) {
        seniorApplicationMasterProperties = new SeniorApplicationMasterProperties(auntAgathaURL);
    }

    public void run() throws IOException, YarnException {
        amRMClient = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient.init(yarnConfiguration);
        amRMClient.start();

        RegisterApplicationMasterResponse response;
        response = amRMClient.registerApplicationMaster(NetUtils.getHostname(), -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());

        yarnClient = YarnClient.createYarnClient();
        yarnClient.init(yarnConfiguration);
        yarnClient.start();
        LOG.info("Connecting to Aunt Agatha: " + seniorApplicationMasterProperties.getAuntAgathaURL());

        metaSchedulerConfig.setServerURL(new java.net.URL(seniorApplicationMasterProperties.getAuntAgathaURL()));
        client = new XmlRpcClient();
        client.setConfig(metaSchedulerConfig);

        fileSystem = FileSystem.get(yarnConfiguration);

        while (true) {
            try {
                doExecutorIter();
            } catch (YarnException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (XmlRpcException e) {
                e.printStackTrace();
            }
            try {
                Thread.sleep(seniorApplicationMasterProperties.getTimeToSleepBetweenIterationsMs());
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }


        /*


        for (int i = 0; i < 5; ++i) {
            YarnClientApplication client = yarnClient.createApplication();
            GetNewApplicationResponse appResponse = client.getNewApplicationResponse();
            ApplicationId appId = appResponse.getApplicationId();
            LOG.info("Applicatoin ID = {}", appId);
            int maxMemory =	appResponse.getMaximumResourceCapability().getMemory();
            int maxVCores =	appResponse.getMaximumResourceCapability().getVirtualCores();
            LOG.info("Max memory = {} and max vcores = {}", maxMemory, maxVCores);
            YarnClusterMetrics clusterMetrics =
                    yarnClient.getYarnClusterMetrics();
            LOG.info("Number of NodeManagers = {}", clusterMetrics.getNumNodeManagers());
            List<NodeReport> nodeReports = yarnClient.getNodeReports(NodeState.RUNNING);
            for (NodeReport node : nodeReports) {
                LOG.info("Node ID = {}, address = {}, containers = {}", node.getNodeId(), node.getHttpAddress(),
                        node.getNumContainers());
            }
            List<QueueInfo> queueList = yarnClient.getAllQueues();
            for (QueueInfo queue : queueList) {
                LOG.info("Available queue: {} with capacity {} to {}", queue.getQueueName(), queue.getCapacity(),
                        queue.getMaximumCapacity());
            }

            Map<String, LocalResource> localResources = new HashMap<String, LocalResource>();
            Map<String, String> env = System.getenv();
            LocalResource appJarFile = Records.newRecord(LocalResource.class);
            appJarFile.setType(LocalResourceType.FILE);
            appJarFile.setVisibility(LocalResourceVisibility.APPLICATION);
            try {
                appJarFile.setResource(ConverterUtils.getYarnUrlFromURI(new URI(env.get("AMJAR"))));
            } catch (URISyntaxException e) {
                e.printStackTrace();
                return;
            }
            appJarFile.setTimestamp(Long.valueOf((env.get("AMJARTIMESTAMP"))));
            appJarFile.setSize(Long.valueOf(env.get("AMJARLEN")));
            localResources.put("app.jar", appJarFile);
            LOG.info("Added {} as a local resource to the Container", appJarFile.toString());

            ApplicationSubmissionContext appContext = client.getApplicationSubmissionContext();
            appContext.setApplicationName("Job Executor " + Integer.toString(i));
            ContainerLaunchContext amContainer = Records.newRecord(ContainerLaunchContext.class);
            amContainer.setLocalResources(localResources);
            amContainer.setEnvironment(env);

            Vector<CharSequence> vargs = new Vector<CharSequence>(30);
            vargs.add(ApplicationConstants.Environment.JAVA_HOME.$() + "/bin/java");
            vargs.add("ru.yandex.cern.yarntest.JobExecutorApplicationMaster");
            vargs.add("1><LOG_DIR>/AM.stdout");
            vargs.add("2><LOG_DIR>/AM.stderr");
            StringBuilder command = new StringBuilder();
            for (CharSequence str : vargs) {
                command.append(str).append(" ");
            }
            List<String> commands = new ArrayList<String>();
            commands.add(command.toString());
            LOG.info("Command to execute ApplicationMaster = {}", command);
            amContainer.setCommands(commands);

            //Request 1024MB of memory for the AM Container
            Resource capability = Records.newRecord(Resource.class);
            capability.setMemory(1024);
            appContext.setResource(capability);

            appContext.setAMContainerSpec(amContainer);
            yarnClient.submitApplication(appContext);
        }
          */

    }

    private long calculateFreeClusterMemory() throws IOException, YarnException {
        long total_memory_available = 0;
        List<NodeReport> nodeReports = yarnClient.getNodeReports();
        for (NodeReport report : nodeReports) {
            total_memory_available += report.getCapability().getMemory() - report.getUsed().getMemory();
        }
        LOG.info("Free cluster memory is: " + Long.toString(total_memory_available));
        return total_memory_available;
    }

    private void doExecutorIter() throws YarnException, IOException, XmlRpcException {
        if (calculateFreeClusterMemory() < seniorApplicationMasterProperties.getMemoryRequiredToStartJeeves())
            return;
        String result = (String) client.execute("GetTask", new Object[]{});
        LOG.info("Got task: " + result);
        if (result.length() == 0)
            return;
        String job_descriptor_path = putJobDescriptorToHDFS(result);
        startJeeves(job_descriptor_path);
        jeeves_task_id += 1;
    }

    private void startJeeves(String job_descriptor_path) throws YarnException, IOException {
        YarnClientApplication client = yarnClient.createApplication();
        GetNewApplicationResponse appResponse = client.getNewApplicationResponse();
        ApplicationId appId = appResponse.getApplicationId();
        LOG.info("Applicatoin ID = {}", appId);

        Map<String, LocalResource> localResources = new HashMap<String, LocalResource>();
        Map<String, String> env = System.getenv();
        LocalResource appJarFile = Records.newRecord(LocalResource.class);
        appJarFile.setType(LocalResourceType.FILE);
        appJarFile.setVisibility(LocalResourceVisibility.APPLICATION);
        try {
            appJarFile.setResource(ConverterUtils.getYarnUrlFromURI(new URI(env.get("AMJAR"))));
        } catch (URISyntaxException e) {
            e.printStackTrace();
            return;
        }
        appJarFile.setTimestamp(Long.valueOf((env.get("AMJARTIMESTAMP"))));
        appJarFile.setSize(Long.valueOf(env.get("AMJARLEN")));
        localResources.put("app.jar", appJarFile);
        LOG.info("Added {} as a local resource to the Container", appJarFile.toString());

        ApplicationSubmissionContext appContext = client.getApplicationSubmissionContext();
        appContext.setApplicationName("Job Executor " + Long.toString(jeeves_task_id));
        ContainerLaunchContext amContainer = Records.newRecord(ContainerLaunchContext.class);
        amContainer.setLocalResources(localResources);
        amContainer.setEnvironment(env);

        Vector<CharSequence> vargs = new Vector<CharSequence>(30);
        vargs.add(ApplicationConstants.Environment.JAVA_HOME.$() + "/bin/java");
        vargs.add("ru.yandex.cern.yarntest.JobExecutorApplicationMaster");
        vargs.add(job_descriptor_path);
        vargs.add("1><LOG_DIR>/AM.stdout");
        vargs.add("2><LOG_DIR>/AM.stderr");
        StringBuilder command = new StringBuilder();
        for (CharSequence str : vargs) {
            command.append(str).append(" ");
        }
        List<String> commands = new ArrayList<String>();
        commands.add(command.toString());
        LOG.info("Command to execute ApplicationMaster = {}", command);
        amContainer.setCommands(commands);

        //Request 1024MB of memory for the AM Container
        Resource capability = Records.newRecord(Resource.class);
        capability.setMemory(1024);
        appContext.setResource(capability);

        appContext.setAMContainerSpec(amContainer);
        yarnClient.submitApplication(appContext);
    }

    private String putJobDescriptorToHDFS(String job_descriptor) throws IOException {
        String pathSuffix = "jeeves_tasks/" + Long.toString(jeeves_task_id);
        Path dest = new Path(fileSystem.getHomeDirectory(), pathSuffix);
        FSDataOutputStream outputStream = fileSystem.create(dest, true);
        outputStream.write(job_descriptor.getBytes());
        outputStream.close();
        LOG.info("Next Jeeves Task was written to " + dest.toString());
        return dest.toString();
    }

    public static void main(String[] args) {
        LOG.info("Starting SeniorApplicationMaster...");
        try {
            SeniorApplicationMaster appMaster = new SeniorApplicationMaster(args[0]);
            appMaster.run();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (YarnException e) {
            e.printStackTrace();
        }
        try {
            Thread.sleep(20000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public class RMCallbackHandler implements AMRMClientAsync.CallbackHandler {

        @Override
        public void onContainersCompleted(List<ContainerStatus> statuses) {
        }

        @Override
        public void onContainersAllocated(List<Container> containers) {
        }

        @Override
        public void onShutdownRequest() {
        }

        @Override
        public void onNodesUpdated(List<NodeReport> updatedNodes) {}

        @Override
        public float getProgress() {
            return 0.0f;
        }

        @Override
        public void onError(Throwable e) {
            amRMClient.stop();
        }

    }

    private class SeniorApplicationMasterProperties {
        public SeniorApplicationMasterProperties(String auntAgathaURL) {
            this.auntAgathaURL = auntAgathaURL;
        }

        public String getAuntAgathaURL() {
            return auntAgathaURL;
        }

        public int getMemoryRequiredToStartJeeves() {
            return 1000;
        }

        public long getTimeToSleepBetweenIterationsMs() {
            return 20000;
        }

        private String auntAgathaURL;
    }
}
