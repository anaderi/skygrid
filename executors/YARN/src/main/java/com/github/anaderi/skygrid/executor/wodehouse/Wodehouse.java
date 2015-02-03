package com.github.anaderi.skygrid.executor.wodehouse;

import com.github.anaderi.skygrid.executor.common.ApplicationMasterExecutor;
import com.github.anaderi.skygrid.executor.common.ApplicationMasterKiller;
import org.apache.commons.cli.*;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.api.records.*;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.apache.hadoop.yarn.exceptions.YarnException;
import org.apache.hadoop.yarn.util.ConverterUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.net.URI;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.ArrayList;

/**
 * Wodehouse is responsible for starting Agathas in other
 * datacenters.
 *
 * It takes path to some datacenter's config and injects
 * Agatha into it.
 */
public class Wodehouse {
    public static void main(String[] args) {
        Option help = OptionBuilder.withLongOpt("help")
                                   .withDescription("display this message")
                                   .create("h");
        Option runAgatha = OptionBuilder.withArgName("metascheduler url")
                                        .hasArg()
                                        .withLongOpt("run-agatha")
                                        .withDescription("Starts in instance of Agatha on YARN cluster")
                                        .create("r");
        Option yarnConfigDir = OptionBuilder.withArgName("path")
                                            .hasArg()
                                            .withLongOpt("yarn-config-dir")
                                            .withDescription("path to YARN conf dir")
                                            .create("c");
        Option killAppId = OptionBuilder.withArgName("AppID")
                                        .hasArg()
                                        .withLongOpt("kill-application")
                                        .withDescription("ApplicationId to be killed")
                                        .create('k');

        Options options = new Options();
        options.addOption(help);
        options.addOption(yarnConfigDir);
        options.addOption(runAgatha);
        options.addOption(killAppId);
        CommandLineParser parser = new PosixParser();
        CommandLine line;
        try {
            line = parser.parse(options, args);
        }
        catch (ParseException exp) {
            System.err.println("Parsing failed.  Reason: " + exp.getMessage());
            return;
        }

        if (line.hasOption("help")) {
            HelpFormatter helpFormatter = new HelpFormatter();
            helpFormatter.printHelp("java com.github.anaderi.skygrid.executor.wodehouse.Wodehouse", options);
            return;
        }

        if (!line.hasOption("c")) {
            System.err.println("-c/--yarn-config-dir argument is obligatory.");
            return;
        }

        try {
            Wodehouse.addPath(line.getOptionValue("c"));
            if (line.hasOption("k")) {
                new ApplicationMasterKiller(line.getOptionValue("k"));
            }
            if (line.hasOption("r")) {
                Wodehouse client = new Wodehouse(line.getOptionValue("r"));
                client.run();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public Wodehouse(String metashedulerURL) throws Exception {
        fileSystem_ = FileSystem.get(new YarnConfiguration());
        metashedulerURL_ = metashedulerURL;
    }

    public void run() throws YarnException, IOException {
        ApplicationMasterExecutor executor = new ApplicationMasterExecutor(
                com.github.anaderi.skygrid.executor.agatha.Agatha.class.getCanonicalName(), APP_NAME);
        ApplicationId applicationId = executor.getApplicationId();
        Path remoteJarPath = copyJarToHDFS(applicationId.toString());
        FileStatus remoteJarStatus = fileSystem_.getFileStatus(remoteJarPath);
        ArrayList<String> extraParams = new ArrayList<String>();
        extraParams.add(metashedulerURL_);
        executor.submitApplication(
                ConverterUtils.getYarnUrlFromPath(remoteJarPath),
                remoteJarStatus.getLen(),
                remoteJarStatus.getModificationTime(),
                extraParams);

    }

    private Path copyJarToHDFS(String agathaAppId) throws IOException {
        Path sourceJarPath = new Path(Wodehouse.class.getProtectionDomain().getCodeSource().getLocation().getFile());
        String destRelativeJarPath = String.format(
                "%s/%s/%s", APP_NAME, agathaAppId, ApplicationMasterExecutor.APP_JAR_NAME);
        Path destJarPath = new Path(fileSystem_.getHomeDirectory(), destRelativeJarPath);
        fileSystem_.copyFromLocalFile(false, true, sourceJarPath, destJarPath);
        LOG.debug("Application Jar is successfully put to HDFS");
        return destJarPath;
    }

    private static void addPath(String s) throws Exception {
        File f = new File(s);
        URI u = f.toURI();
        URLClassLoader urlClassLoader = (URLClassLoader) ClassLoader.getSystemClassLoader();
        Class<URLClassLoader> urlClass = URLClassLoader.class;
        Method method = urlClass.getDeclaredMethod("addURL", new Class[]{URL.class});
        method.setAccessible(true);
        method.invoke(urlClassLoader, new Object[]{u.toURL()});
    }

    private static final Logger LOG = LoggerFactory.getLogger(Wodehouse.class);
    private static final String APP_NAME = "SkygridExecutor.Agatha";
    private final String metashedulerURL_;

    private FileSystem fileSystem_;
}
