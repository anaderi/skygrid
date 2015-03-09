package com.github.anaderi.skygrid.executor.wooster;

import com.github.anaderi.skygrid.Cube;
import com.github.anaderi.skygrid.executor.common.JobDescriptor;
import com.github.anaderi.skygrid.executor.common.WoosterBusynessSubscriber;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.api.ApplicationConstants;
import org.apache.hadoop.yarn.api.protocolrecords.RegisterApplicationMasterResponse;
import org.apache.hadoop.yarn.api.records.*;
import org.apache.hadoop.yarn.client.api.AMRMClient;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync;
import org.apache.hadoop.yarn.client.api.async.NMClientAsync;
import org.apache.hadoop.yarn.client.api.async.impl.NMClientAsyncImpl;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.apache.hadoop.yarn.util.Records;
import org.codehaus.jackson.map.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.imageio.IIOException;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.ByteBuffer;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.*;

/**
 * Woosters responsibility is receiving new tasks,
 * informing Agatha about it, splitting it and giving
 * it to a appropriate number of Jeeves.
 */
public class Wooster {
    private static final Logger LOG = LoggerFactory.getLogger(Wooster.class);
    private AMRMClientAsync<AMRMClient.ContainerRequest> amRMClient_;
    private NMClientAsyncImpl nmClient_;
    private NMCallbackHandler containerListener_;
    private final String metaSchedulerURL_;
    private final int SLEEP_BETWEEN_POLLING = 10000;
    private final int FAILED_COUNTER_THRESHOLD = 3;
    private final List<Thread> containerLaunchingThreads_ = new LinkedList<Thread>();
    private final HashMap<ContainerId, String> processingDescriptors_ = new HashMap<ContainerId, String>();
    private final HashMap<Integer, Integer> failureCounter_ = new HashMap<Integer, Integer>();
    private final HashMap<String, JobDescriptor> containerToJobDescriptors_ = new HashMap<String, JobDescriptor>();
    private final YarnConfiguration yarnConfiguration_ = new YarnConfiguration();
    private int totalContainersCount_ = 1;
    private String agathaHostname_;
    private String taskUUID_;
    private final JobDescriptorProcessingQueue processingQueue_ = new JobDescriptorProcessingQueue();

    public static void main(String[] args) throws InterruptedException {
        try {
            new Wooster(args[0], args[1]);
        } catch (Exception e) {
            e.printStackTrace();
            Thread.sleep(120000);
        }
    }

    public Wooster(String agathaHostname, String metaSchedulerURL) throws IOException, YarnException, NotBoundException, InterruptedException {
        agathaHostname_ = agathaHostname;
        amRMClient_ = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient_.init(yarnConfiguration_);
        amRMClient_.start();

        containerListener_ = new NMCallbackHandler();
        nmClient_ = new NMClientAsyncImpl(containerListener_);
        nmClient_.init(yarnConfiguration_);
        nmClient_.start();

        metaSchedulerURL_ = metaSchedulerURL;
        taskUUID_ = UUID.randomUUID().toString();

        RegisterApplicationMasterResponse response;
        response = amRMClient_.registerApplicationMaster(NetUtils.getHostname(), -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());

        RemoteQueue input_queue = new RemoteQueue("http://metascheduler.test.vs.os.yandex.net/", "stromsund-a");
        JobDescriptor jd = null;

        while (true) {
            try {
                LOG.info("Connecting to MetaScheduler");
                jd = input_queue.getTask();
                if (jd != null)
                    break;
            } catch (Exception e) {
                LOG.info("Connection error!");
                break;
            }
            LOG.info("Waiting for a job...");
            Thread.sleep(SLEEP_BETWEEN_POLLING);
        }

        while (true) {
            try {
                // We must inform Agatha anyway.
                informAgathaAboutWoosterIsBusy();
                break;
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        // In case of connection problems.
        if (jd == null)
            return;

        LOG.info("Wooster got job: {}", jd);
        processingQueue_.AppendJobDescriptor(jd);
        requestContainers(processingQueue_.UpcomingQueueSize());

        while (true) {
            synchronized (processingQueue_) {
                if (processingQueue_.IsCompletedSuccsessfully())
                    break;
            }
            LOG.info("Jeeveses are still working");
            Thread.sleep(7000);
        }
        amRMClient_.unregisterApplicationMaster(FinalApplicationStatus.SUCCEEDED, "ok", "ok");
    }

    public void informAgathaAboutWoosterIsBusy() throws NotBoundException, RemoteException {
        String agathaIP = agathaHostname_.split("/")[1];
        LOG.info("Sending onWoosterBusy to {}", agathaIP);
        Registry registry = LocateRegistry.getRegistry(agathaIP, 25497);
        WoosterBusynessSubscriber subscriber = (WoosterBusynessSubscriber)registry.lookup("WoosterBusynessSubscriber");
        subscriber.onWoosterBusy();
    }

    private void requestContainers(int amount) {
        for (int i = 0; i < amount; ++i) {
            AMRMClient.ContainerRequest containerAsk = setupContainerAskForRM();
            amRMClient_.addContainerRequest(containerAsk);
        }
    }

    private AMRMClient.ContainerRequest setupContainerAskForRM() {
        Priority pri = Records.newRecord(Priority.class);
        pri.setPriority(0);
        Resource capability = Records.newRecord(Resource.class);
        capability.setMemory(128);
        capability.setVirtualCores(1);

        AMRMClient.ContainerRequest request = new AMRMClient.ContainerRequest(capability, null, null, pri);
        LOG.info("Requested container ask: " + request.toString());
        return request;
    }

    public class RMCallbackHandler implements AMRMClientAsync.CallbackHandler {
        @Override
        public void onContainersCompleted(List<ContainerStatus> statuses) {
            LOG.info("onContainersCompleted on thread {}", Thread.currentThread());
            for (ContainerStatus status : statuses) {

                LOG.info("Completion status for container {}: {} ({})", status.getContainerId(),
                        status.getExitStatus(), status.getDiagnostics());
                processingQueue_.MarkJobDescriptorAsCompleted(containerToJobDescriptors_.get(status.getContainerId().toString()));
                /*
                String currentJobSerialized;
                JobDescriptor currentJob;
                synchronized (processingDescriptors_) {
                    currentJobSerialized = processingDescriptors_.get(status.getContainerId());
                    processingDescriptors_.remove(status.getContainerId());
                }
                try {
                    currentJob = JobDescriptor.fromJsonString(currentJobSerialized);
                } catch (JobDescriptor.JobDescriptorFormatException e) {
                    LOG.error("Wow! I was unable to parse JSON I've created recently! {}",
                            processingDescriptors_.get(status.getContainerId()));
                    continue;
                } catch (IOException e) {
                    LOG.error("IOError on parsing JSON from processingDescriptors_.");
                    continue;
                }
                if (status.getExitStatus() != 0) {
                    Integer counter = 0;
                    Integer job_index = processingQueue_.FindJobDescriptorIndex(currentJob);
                    if (failureCounter_.containsKey(job_index)) {
                        counter = failureCounter_.get(job_index);
                    }
                    failureCounter_.put(job_index, counter);
                    if (counter < FAILED_COUNTER_THRESHOLD) {
                        processingQueue_.MarkJobDescriptorAsFailed(currentJob);
                        requestContainers(1);
                    }
                } else {
                    processingQueue_.MarkJobDescriptorAsCompleted(currentJob);
                }
                */
            }
        }

        @Override
        public void onContainersAllocated(List<Container> containers) {
            LOG.info("onContainersAllocated on thread {}", Thread.currentThread());
            int count = 0;
            for (Container container : containers) {
                JobDescriptor jobDescriptor = processingQueue_.GetNextTask();
                ++count;
                containerToJobDescriptors_.put(container.getId().toString(), jobDescriptor);
                ContainerLauncher launcher = new ContainerLauncher(container, jobDescriptor);
                Thread launchingThread = new Thread(launcher);
                containerLaunchingThreads_.add(launchingThread);
                launchingThread.start();
            }
            LOG.info("Allocated {} containers", count);
        }

        @Override
        public void onShutdownRequest() {
            LOG.info("onShutdownRequest");
        }

        @Override
        public void onNodesUpdated(List<NodeReport> updatedNodes) {
            LOG.info("onNodesUpdated");
        }

        @Override
        public float getProgress() {
            return 1.0f * processingQueue_.UpcomingQueueSize() / totalContainersCount_;
        }

        @Override
        public void onError(Throwable e) {
            amRMClient_.stop();
        }
    }

    class ContainerLauncher implements Runnable {
        private Container allocatedContainer_;
        private JobDescriptor jobDescriptor_;
        public static final String APP_JAR_NAME = "app.jar";

        ContainerLauncher(Container allocatedContainer, JobDescriptor jobDescriptor) {
            this.allocatedContainer_ = allocatedContainer;
            this.jobDescriptor_ = jobDescriptor;
        }

        private Map<String, LocalResource> getApplicationsResources() throws IOException {
            LocalResource jarResource = Records.newRecord(LocalResource.class);

            Map<String, String> env = System.getenv();
            String[] url_paths = env.get("AMJAR").split(" ");
            org.apache.hadoop.yarn.api.records.URL jarToExecute = org.apache.hadoop.yarn.api.records.URL.newInstance(
                    url_paths[1], url_paths[3], Integer.valueOf(url_paths[5]), url_paths[7]);

            jarResource.setResource(jarToExecute);
            jarResource.setSize(Long.valueOf(env.get("AMJARLEN")));
            jarResource.setTimestamp(Long.valueOf(env.get("AMJARTIMESTAMP")));
            jarResource.setType(LocalResourceType.FILE);
            jarResource.setVisibility(LocalResourceVisibility.APPLICATION);
            Map<String, LocalResource> localResources = new HashMap<String, LocalResource>();
            localResources.put(APP_JAR_NAME, jarResource);
            return localResources;
        }

        private String getApplicationsClasspath() {
            StringBuilder classPathEnv = new StringBuilder().append(File.pathSeparatorChar).append("./" + APP_JAR_NAME);
            for (String c : yarnConfiguration_.getStrings(YarnConfiguration.YARN_APPLICATION_CLASSPATH,
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
            env.put("CLASSPATH", getApplicationsClasspath());
            return env;
        }

        private String generateUrlForJobDescriptor() {
            return String.format("Woosters/%s/%s", taskUUID_, jobDescriptor_.job.job_id);
        }

        @Override
        public void run() {
            String job_descriptor_encoded;
            try {
                // $ getconf ARG_MAX
                // 262144
                // so, about 250kB may be transferred as a job descriptor.
                ObjectMapper mapper = new ObjectMapper();
                String jd_json = mapper.writeValueAsString(jobDescriptor_);
                job_descriptor_encoded = URLEncoder.encode(jd_json, "UTF-8");
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
                return;
            } catch (IOException e) {
                e.printStackTrace();
                return;
            }

            LOG.info("Starting container on thread {}", Thread.currentThread());
            Vector<CharSequence> vargs = new Vector<CharSequence>(5);
            vargs.add(ApplicationConstants.Environment.JAVA_HOME.$() + "/bin/java");
            vargs.add(com.github.anaderi.skygrid.executor.jeeves.Jeeves.class.getCanonicalName());
            vargs.add(job_descriptor_encoded);
            vargs.add(generateUrlForJobDescriptor());
            vargs.add("1><LOG_DIR>/AM.stdout");
            vargs.add("2><LOG_DIR>/AM.stderr");
            // Get final commmand
            StringBuilder command = new StringBuilder();
            for (CharSequence str : vargs) {
                command.append(str).append(" ");
            }

            List<String> commands = new ArrayList<String>();
            commands.add(command.toString());

            ContainerLaunchContext ctx = null;
            try {
                ctx = ContainerLaunchContext.newInstance(
                        getApplicationsResources(),
                        getApplicationsEnvironment(),
                        commands,
                        null, null, null);
            } catch (IOException e) {
                e.printStackTrace();
            }
            nmClient_.startContainerAsync(allocatedContainer_, ctx);
        }
    }
}
