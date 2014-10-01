package com.github.anaderi.skygrid.executor.agatha;

import com.github.anaderi.skygrid.executor.common.ApplicationMasterExecutor;
import com.github.anaderi.skygrid.executor.common.WoosterBusynessSubscriber;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.api.protocolrecords.RegisterApplicationMasterResponse;
import org.apache.hadoop.yarn.api.records.*;
import org.apache.hadoop.yarn.client.api.AMRMClient;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.*;
import java.rmi.AlreadyBoundException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Semaphore;

/**
 *  Agatha starts Wooster and freezes until Wooster got a job.
 *  As soon as Wooster got a job, he notificates her, and she
 *  starts a new instance of Wooster.
 */
public class Agatha implements WoosterBusynessSubscriber {

    public static void main(String[] args) throws IOException, YarnException, AlreadyBoundException, URISyntaxException, InterruptedException {
        Agatha agatha = new Agatha(args[0]);
        WoosterBusynessSubscriber stub = (WoosterBusynessSubscriber)UnicastRemoteObject.exportObject(agatha, 0);
        Registry registry = LocateRegistry.createRegistry(25497);
        registry.bind("WoosterBusynessSubscriber", stub);
        agatha.run();
    }

    public Agatha(String metaschedulerURL) throws IOException, YarnException {
        String APP_NAME = "SkygridExecutor.Wooster";
        agathasHostname_ = NetUtils.getHostname();
        metaschedulerURL_ = metaschedulerURL;
        executor_ = new ApplicationMasterExecutor(
                com.github.anaderi.skygrid.executor.wooster.Wooster.class.getCanonicalName(),
                APP_NAME);
    }

    private void run() throws IOException, YarnException, URISyntaxException, InterruptedException {
        amRMClient_ = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient_.init(yarnConfiguration_);
        amRMClient_.start();

        RegisterApplicationMasterResponse response;
        response = amRMClient_.registerApplicationMaster(agathasHostname_, -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());

        while (true) {
            busyWoostersCounter_.acquire();
            executeWooster();
        }

        // amRMClient.unregisterApplicationMaster(FinalApplicationStatus.SUCCEEDED, "ok", "ok");
    }

    @Override
    public void onWoosterBusy() {
        LOG.info("Oh, Wooster is busy. On thread {}", Thread.currentThread());
        busyWoostersCounter_.release();
    }

    private void executeWooster() throws YarnException, IOException, URISyntaxException {
        LOG.info("Executing Wooster on thread {}", Thread.currentThread());
        Map<String, String> env = System.getenv();
        String[] url_paths = env.get("AMJAR").split(" ");
        org.apache.hadoop.yarn.api.records.URL jarToExecute = org.apache.hadoop.yarn.api.records.URL.newInstance(
                url_paths[1], url_paths[3], Integer.valueOf(url_paths[5]), url_paths[7]);
        List<String> extra_args_to_wooster = new ArrayList<String>();
        extra_args_to_wooster.add(agathasHostname_);
        extra_args_to_wooster.add(metaschedulerURL_);
        executor_.startApplication(
                jarToExecute,
                Long.valueOf(env.get("AMJARLEN")),
                Long.valueOf(env.get("AMJARTIMESTAMP")),
                extra_args_to_wooster);
    }

    private static final Logger LOG = LoggerFactory.getLogger(Agatha.class);
    private final YarnConfiguration yarnConfiguration_ = new YarnConfiguration();
    private AMRMClientAsync<AMRMClient.ContainerRequest> amRMClient_;
    private String agathasHostname_;
    private final ApplicationMasterExecutor executor_;
    private final String metaschedulerURL_;

    // 1 because we need to start Wooster on startup.
    private Semaphore busyWoostersCounter_ = new Semaphore(1);

    public class RMCallbackHandler implements AMRMClientAsync.CallbackHandler {
        @Override
        public void onContainersCompleted(List<ContainerStatus> statuses) {
            LOG.debug("onContainersCompleted");
        }

        @Override
        public void onContainersAllocated(List<Container> containers) {
            LOG.debug("onContainersAllocated");
        }

        @Override
        public void onShutdownRequest() {
            LOG.debug("onShutdownRequest");
        }

        @Override
        public void onNodesUpdated(List<NodeReport> updatedNodes) {
            LOG.debug("onNodesUpdated");
        }

        @Override
        public float getProgress() {
            return 0.0f;
        }

        @Override
        public void onError(Throwable e) {
            amRMClient_.stop();
        }
    }
}
