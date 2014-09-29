package com.github.anaderi.skygrid.executor.wodehouse;

import com.github.anaderi.skygrid.executor.common.ApplicationMasterExecutor;
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
        Wodehouse client;
        if (args.length != 2) {
            System.out.println("Obligatory arguments: path to YarnConfig, MetaScheduler URL");
            return;
        }

        try {
            client = new Wodehouse(args[0], args[1]);
            client.run();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public Wodehouse(String yarnConfigPath, String metashedulerURL) throws Exception {
        addPath(yarnConfigPath);
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
                "%s/%s/%s",APP_NAME, agathaAppId, ApplicationMasterExecutor.APP_JAR_NAME);
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
