package com.github.anaderi.skygrid.executor.jeeves;

import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.conf.YarnConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;

/**
 * Created by stromsund on 25/01/15.
 */
public class Jeeves {

    public static void main(String[] args) throws InterruptedException, IOException {
        System.out.println("Hello, world!");
        try {
            String task = URLDecoder.decode(args[0], "UTF-8");
            String url_to_put_result = args[1];
            System.out.println(task);

            FileSystem fileSystem = FileSystem.get(new YarnConfiguration());
            Path p = new Path(url_to_put_result);
            FSDataOutputStream file = fileSystem.create(p);
            file.writeChars(task);
            file.flush();
            file.close();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        System.out.flush();
        Thread.sleep(60000);
    }
}
