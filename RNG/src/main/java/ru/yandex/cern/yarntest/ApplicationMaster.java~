package ru.yandex.cern.yarntest;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.hadoop.fs.BlockLocation;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.api.ApplicationConstants.Environment;
import org.apache.hadoop.yarn.api.protocolrecords.RegisterApplicationMasterResponse;
import org.apache.hadoop.yarn.api.records.Container;
import org.apache.hadoop.yarn.api.records.ContainerLaunchContext;
import org.apache.hadoop.yarn.api.records.ContainerStatus;
import org.apache.hadoop.yarn.api.records.FinalApplicationStatus;
import org.apache.hadoop.yarn.api.records.LocalResource;
import org.apache.hadoop.yarn.api.records.LocalResourceType;
import org.apache.hadoop.yarn.api.records.LocalResourceVisibility;
import org.apache.hadoop.yarn.api.records.NodeReport;
import org.apache.hadoop.yarn.api.records.Priority;
import org.apache.hadoop.yarn.api.records.Resource;
import org.apache.hadoop.yarn.client.api.AMRMClient.ContainerRequest;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync;
import org.apache.hadoop.yarn.client.api.async.AMRMClientAsync.CallbackHandler;
import org.apache.hadoop.yarn.client.api.async.NMClientAsync;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.apache.hadoop.yarn.util.ConverterUtils;
import org.apache.hadoop.yarn.util.Records;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class ApplicationMaster {

    private static final Logger LOG =
            LoggerFactory.getLogger(ApplicationMaster.class);
    private YarnConfiguration conf;
    private AMRMClientAsync<ContainerRequest> amRMClient;
    private FileSystem fileSystem;
    private int numOfContainers;
    protected AtomicInteger numCompletedContainers =
            new AtomicInteger();
    private volatile boolean done;
    protected NMClientAsync nmClient;
    private NMCallbackHandler containerListener;
    private List<Thread> launchThreads = new ArrayList<Thread>();
    private Path inputFile;
    private String minNumber;
    private String maxNumber;
    private int numberOfContainers;
    private int numbersPerContainer;
    private String outputFilename;
    private Integer last_calculated_value = new Integer(0);

    public ApplicationMaster(String [] args) throws IOException {
        conf = new YarnConfiguration();
        fileSystem = FileSystem.get(conf);
        inputFile = new Path(args[0]);
        minNumber = args[1];
        maxNumber = args[2];
        numberOfContainers = Integer.parseInt(args[3]);
        numbersPerContainer = Integer.parseInt(args[4]);
        outputFilename = args[5];
    }

    public BlockLocation[] getBlockLocations() throws IOException {
        // Read the block information from HDFS
        FileStatus fileStatus =
                fileSystem.getFileStatus(inputFile);
        LOG.info("File status = {}", fileStatus.toString());
        BlockLocation[] blocks =
                fileSystem.getFileBlockLocations(fileStatus, 0,
                        fileStatus.getLen());
        LOG.info("Number of blocks for {} = {}",
                inputFile.toString(), blocks.length);
        return blocks;
    }

    public void run() throws YarnException, IOException {
        amRMClient = AMRMClientAsync.createAMRMClientAsync(1000, new RMCallbackHandler());
        amRMClient.init(conf);
        amRMClient.start();

        RegisterApplicationMasterResponse response;
        response = amRMClient.registerApplicationMaster(NetUtils.getHostname(), -1, "");
        LOG.info("ApplicationMaster is registered with response: {}", response.toString());

        containerListener = new NMCallbackHandler(this);
        nmClient = NMClientAsync.createNMClientAsync(containerListener);
        nmClient.init(conf);
        nmClient.start();

        Resource capacity = Records.newRecord(Resource.class);
        capacity.setMemory(128);
        Priority priority = Records.newRecord(Priority.class);
        priority.setPriority(0);
		for(int i = 1; i <= numberOfContainers; i++) {
			ContainerRequest ask = new ContainerRequest(capacity,null, null,priority);
			amRMClient.addContainerRequest(ask);
			numOfContainers++;
		}
        /*
        BlockLocation [] blocks = this.getBlockLocations();
        for (BlockLocation block : blocks) {
            ContainerRequest ask = new ContainerRequest(capacity, block.getHosts(), null, priority, false);
            numOfContainers++;
            amRMClient.addContainerRequest(ask);
            blockList.add(new BlockStatus(block));
            LOG.info("Asking for Container for block {}", block.toString());
        }
        */

        while(!done && numCompletedContainers.get() < numOfContainers) {
            LOG.info("The number of completed Containers = " +
                    this.numCompletedContainers.get());
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        // Join all launched threads: needed for when we time
        // out and we need to release containers
        for (Thread launchThread : launchThreads) {
            try {
                launchThread.join(10000);
            }
            catch (InterruptedException e) {
                LOG.info("Exception thrown in thread join: {}",
                        e.getMessage());
                e.printStackTrace();
            }
        }

        LOG.info("Containers have all completed, so shutting down NMClient and AMRMClient...");

        nmClient.stop();
        amRMClient.unregisterApplicationMaster(FinalApplicationStatus.SUCCEEDED, "Application complete!", null);
        amRMClient.stop();

    }

    public static void main(String[] args) {
        LOG.info("Starting ApplicationMaster...");

        try {
            ApplicationMaster appMaster = new ApplicationMaster(args);
            appMaster.run();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (YarnException e) {
            e.printStackTrace();
        }
    }

    protected class ContainerLauncher implements Runnable {
        private Container container;
        private NMCallbackHandler containerListener;

        public ContainerLauncher(Container container,
                                 NMCallbackHandler containerListener) {
            super();
            this.container = container;
            this.containerListener = containerListener;
        }

        @Override
        public void run() {
            LOG.info("Setting up ContainerLauncher for containerid = {}", container.getId());
            Map<String, LocalResource> localResources = new HashMap<String, LocalResource>();
            Map<String, String> env = System.getenv();
            LocalResource appJarFile =
                    Records.newRecord(LocalResource.class);
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
            LOG.info("Added {} as a local resource to the Container",
                    appJarFile.toString());

            ContainerLaunchContext context = Records.newRecord(ContainerLaunchContext.class);
            context.setEnvironment(env);
            context.setLocalResources(localResources);
            String command = null;
            try {
                command = this.getLaunchCommand(container);
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            List<String> commands = new ArrayList<String>();
            commands.add(command);
            context.setCommands(commands);
            LOG.info("Command to execute Container = {}", command);

            nmClient.startContainerAsync(container, context);
            LOG.info("Container {} launched!", container.getId());
        }

        public String getLaunchCommand(Container container) throws IOException {
            Integer current_value;
            synchronized (last_calculated_value) {
                current_value = last_calculated_value;
                last_calculated_value += numbersPerContainer;
            }

            Vector<CharSequence> vargs = new Vector<CharSequence>(30);
            vargs.add(Environment.JAVA_HOME.$() + "/bin/java");
            vargs.add("ru.yandex.cern.yarntest.MyContainer ");
            vargs.add(inputFile.toString()); // File to read

            String offsetString =
                    Long.toString(current_value);
            String lengthString =
                    Long.toString(last_calculated_value);
            LOG.info("Calculating primes in block {} : {}",
                    offsetString, lengthString);
            vargs.add(offsetString); // Offset into the file
            vargs.add(lengthString); // Number of bytes to read
            vargs.add(minNumber);
            vargs.add(maxNumber);
            vargs.add(outputFilename);
            vargs.add("1><LOG_DIR>/MyContainer.stdout");
            vargs.add("2><LOG_DIR>/MyContainer.stderr");
            StringBuilder command = new StringBuilder();
            for (CharSequence str : vargs) {
                command.append(str).append(" ");
            }
            return command.toString();

        }
    }

    public class RMCallbackHandler implements CallbackHandler {

        @Override
        public void onContainersCompleted(List<ContainerStatus> statuses) {
            LOG.info("Got response from RM for container ask, completed	count = {}", statuses.size());
            for(ContainerStatus status : statuses) {
                numCompletedContainers.incrementAndGet();
                LOG.info("Container completed : {}", status.getContainerId());
            }
        }

        @Override
        public void onContainersAllocated(List<Container> containers) {
            LOG.info("Got response from RM for container ask, allocated	count = {}", containers.size());
            for(Container container : containers) {
                LOG.info("Starting Container on {}", container.getNodeHttpAddress());
                ContainerLauncher launcher = new ContainerLauncher(container, containerListener);
                Thread thread = new Thread(launcher);
                thread.start();
                launchThreads.add(thread);

	/*			ContainerLaunchContext context = Records.newRecord(ContainerLaunchContext.class);
				int random = (int) (Math.random() * 30);
				String command = "sleep " + random;
				LOG.info("Container command is {}", command);
				List<String> commands = new ArrayList<>();
				commands.add(command);
				
				context.setCommands(commands);
				LOG.info("Starting Container {}", container.getId());
				nmClient.startContainerAsync(container, context);
	*/
            }
        }

        @Override
        public void onShutdownRequest() {
            done = true;
        }

        @Override
        public void onNodesUpdated(List<NodeReport> updatedNodes) {}

        @Override
        public float getProgress() {
            float progress = numOfContainers <= 0 ? 0 : (float) numCompletedContainers.get() / numOfContainers;
            return progress;
        }

        @Override
        public void onError(Throwable e) {
            done = true;
            amRMClient.stop();
        }

    }

}
