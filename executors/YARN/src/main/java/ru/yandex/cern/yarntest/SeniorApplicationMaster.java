package ru.yandex.cern.yarntest;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.api.ApplicationConstants;
import org.apache.hadoop.yarn.api.protocolrecords.GetNewApplicationResponse;
import org.apache.hadoop.yarn.api.protocolrecords.RegisterApplicationMasterResponse;
import org.apache.hadoop.yarn.api.records.*;
import org.apache.hadoop.yarn.client.api.AMRMClient;
import org.apache.hadoop.yarn.client.api.YarnClient;
import org.apache.hadoop.yarn.client.api.YarnClientApplication;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.apache.hadoop.yarn.util.ConverterUtils;
import org.apache.hadoop.yarn.util.Records;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Created by stromsund on 02.08.14.
 */
public class SeniorApplicationMaster {
    private static final Logger LOG =
            LoggerFactory.getLogger(ApplicationMaster.class);
    private YarnConfiguration conf;
    private AMRMClientAsync<AMRMClient.ContainerRequest> amRMClient;
    protected AtomicInteger num_of_started_containers = new AtomicInteger(0);

    public SeniorApplicationMaster(String [] args) throws IOException {
        conf = new YarnConfiguration();
    }

    public void run() throws IOException, YarnException {
        amRMClient = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient.init(conf);
        amRMClient.start();

        RegisterApplicationMasterResponse response;
        response = amRMClient.registerApplicationMaster(NetUtils.getHostname(), -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());

        YarnClient yarnClient;
        yarnClient = YarnClient.createYarnClient();
        yarnClient.init(conf);
        yarnClient.start();
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

            num_of_started_containers.incrementAndGet();
        }

        amRMClient.unregisterApplicationMaster(FinalApplicationStatus.SUCCEEDED, "Application complete!", null);
        amRMClient.stop();
    }

    public static void main(String[] args) {
        LOG.info("Starting SeniorApplicationMaster...");

        try {
            SeniorApplicationMaster appMaster = new SeniorApplicationMaster(args);
            appMaster.run();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (YarnException e) {
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
            return num_of_started_containers.get() / 5.0f;
        }

        @Override
        public void onError(Throwable e) {
            amRMClient.stop();
        }

    }
}
