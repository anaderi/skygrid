package com.github.anaderi.skygrid.executor.wooster;

import com.github.anaderi.skygrid.executor.common.WoosterBusynessSubscriber;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.api.protocolrecords.RegisterApplicationMasterResponse;
import org.apache.hadoop.yarn.api.records.Container;
import org.apache.hadoop.yarn.api.records.ContainerStatus;
import org.apache.hadoop.yarn.api.records.FinalApplicationStatus;
import org.apache.hadoop.yarn.api.records.NodeReport;
import org.apache.hadoop.yarn.client.api.AMRMClient;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.List;

/**
 * Woosters responsibility is receiving new tasks,
 * informing Agatha about it, splitting it and giving
 * it to a appropriate number of Jeeves.
 */
public class Wooster {
    private static final Logger LOG = LoggerFactory.getLogger(Wooster.class);
    private AMRMClientAsync<AMRMClient.ContainerRequest> amRMClient_;
    private final String metaSchedulerURL_;
    private final int SLEEP_BETWEEN_POLLING = 1000;

    public static void main(String[] args) throws IOException, YarnException, NotBoundException, InterruptedException {
        new Wooster(args[1]);
    }

    public Wooster(String metaSchedulerURL) throws IOException, YarnException, NotBoundException, InterruptedException {
        YarnConfiguration yarnConfiguration_ = new YarnConfiguration();
        amRMClient_ = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient_.init(yarnConfiguration_);
        amRMClient_.start();
        metaSchedulerURL_ = metaSchedulerURL;

        RegisterApplicationMasterResponse response;
        response = amRMClient_.registerApplicationMaster(NetUtils.getHostname(), -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());

        boolean gotJob = false;
        String jobDescription = "";
        while (!gotJob) {
            URL url = new URL(metaSchedulerURL_ + "/queues/main");
            HttpURLConnection connection = (HttpURLConnection)url.openConnection();
            connection.setRequestMethod("GET");
            connection.connect();
            InputStream stream = connection.getInputStream();
            BufferedReader in = new BufferedReader(new InputStreamReader(stream));
            jobDescription = "";
            for (String x = in.readLine(); x != null; x = in.readLine()) {
                if (x.contains("description")) {
                    gotJob = true;
                    break;
                }
                jobDescription += x;
            }
           Thread.sleep(SLEEP_BETWEEN_POLLING);
        }

        LOG.info("Wooster got job: {}", jobDescription);
        Thread.sleep(20000);
        informAgathaAboutWoosterIsBusy();
        amRMClient_.unregisterApplicationMaster(FinalApplicationStatus.SUCCEEDED, "ok", "ok");
    }

    public static void informAgathaAboutWoosterIsBusy() throws NotBoundException, RemoteException {
        Registry registry = LocateRegistry.getRegistry("master.local", 25497);
        WoosterBusynessSubscriber subscriber = (WoosterBusynessSubscriber)registry.lookup("WoosterBusynessSubscriber");
        subscriber.onWoosterBusy();
    }

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
