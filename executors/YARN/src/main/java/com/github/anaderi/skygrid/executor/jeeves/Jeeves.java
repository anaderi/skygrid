package com.github.anaderi.skygrid.executor.jeeves;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;

/**
 * Created by stromsund on 25/01/15.
 */
public class Jeeves {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("Hello, world!");
        try {
            String task = URLDecoder.decode(args[0], "UTF-8");
            System.out.println(task);
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        System.out.flush();
        Thread.sleep(60000);
    }
}
