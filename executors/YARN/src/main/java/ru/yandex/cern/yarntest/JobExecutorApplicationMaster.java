package ru.yandex.cern.yarntest;

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

import java.io.IOException;
import java.util.List;

/**
 * Created by stromsund on 02.08.14.
 */
public class JobExecutorApplicationMaster {
    private static final Logger LOG =
            LoggerFactory.getLogger(ApplicationMaster.class);
    private YarnConfiguration conf;
    private AMRMClientAsync<AMRMClient.ContainerRequest> amRMClient;

    public JobExecutorApplicationMaster(String [] args) {
        conf = new YarnConfiguration();
    }

    public void run() throws IOException, YarnException {
        amRMClient = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient.init(conf);
        amRMClient.start();

        RegisterApplicationMasterResponse response;
        response = amRMClient.registerApplicationMaster(NetUtils.getHostname(), -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());
        amRMClient.unregisterApplicationMaster(FinalApplicationStatus.SUCCEEDED, "Application complete!", null);
        amRMClient.stop();
    }

    public static void main(String[] args) {
        LOG.info("Starting JobExecutorApplicationMaster...");

        try {
            JobExecutorApplicationMaster appMaster = new JobExecutorApplicationMaster(args);
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
            return 0.5f;
        }

        @Override
        public void onError(Throwable e) {
            amRMClient.stop();
        }

    }
}
