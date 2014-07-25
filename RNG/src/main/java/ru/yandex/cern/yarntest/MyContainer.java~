package ru.yandex.cern.yarntest;

import java.io.IOException;
import java.util.Random;

import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MyContainer {
    private static final Logger LOG = LoggerFactory.getLogger(MyContainer.class);
    private String hostname;
    private YarnConfiguration conf;
    private FileSystem fs;
    private Path inputFile;
    private long start;
    private int stop;
    private int minNumber;
    private int maxNumber;
    private String outputFilename;

    public MyContainer(String[] args) throws IOException {
        hostname = NetUtils.getHostname();
        conf = new YarnConfiguration();
        fs = FileSystem.get(conf);
        inputFile = new Path(args[0]);
        start = Long.parseLong(args[1]);
        stop = Integer.parseInt(args[2]);
        minNumber = Integer.parseInt(args[3]);
        maxNumber = Integer.parseInt(args[4]);
        outputFilename = args[5];
    }

    public static void main(String[] args) {
        LOG.info("Container just started on {}", NetUtils.getHostname());
        try {
            MyContainer container = new MyContainer(args);
            container.run();
        } catch (IOException e) {
            e.printStackTrace();
        }
        LOG.info("Container is ending...");
    }

    private void run() throws IOException {
        LOG.info("Running Container on {}", this.hostname);
        FSDataOutputStream output = fs.create(
                new Path("hdfs://master.local:9000/user/yarnuser/CernYarnApp/generatedNumbers/"+outputFilename + start + "-" + stop));
        Random rand = new Random();
        for (long current = start; current < stop; ++current) {
            Integer randomNumber = minNumber + rand.nextInt((maxNumber - minNumber) + 1);
            String report = randomNumber.toString() + "\n";
            output.write(report.getBytes());
        }
        output.close();
    }

}
