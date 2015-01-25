package com.github.anaderi.skygrid.executor.wooster;

import org.apache.hadoop.yarn.api.records.ContainerId;
import org.apache.hadoop.yarn.api.records.ContainerStatus;
import org.apache.hadoop.yarn.client.api.async.NMClientAsync;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.ByteBuffer;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

public class NMCallbackHandler implements NMClientAsync.CallbackHandler {
    private static final Logger LOG = LoggerFactory.getLogger(NMCallbackHandler.class);

    @Override
    public void onContainerStarted(ContainerId containerId, Map<String, ByteBuffer> stringByteBufferMap) {
        LOG.info("Jeeves {} started (on thread {})", containerId, Thread.currentThread());
    }

    @Override
    public void onContainerStatusReceived(ContainerId containerId, ContainerStatus containerStatus) {

    }

    @Override
    public void onContainerStopped(ContainerId containerId) {
        LOG.info("Jeeves {} stopped (on thread {})", containerId, Thread.currentThread());
    }

    @Override
    public void onStartContainerError(ContainerId containerId, Throwable throwable) {
        LOG.info("Jeeves {} was unable to start", containerId);
    }

    @Override
    public void onGetContainerStatusError(ContainerId containerId, Throwable throwable) {

    }

    @Override
    public void onStopContainerError(ContainerId containerId, Throwable throwable) {

    }
}
