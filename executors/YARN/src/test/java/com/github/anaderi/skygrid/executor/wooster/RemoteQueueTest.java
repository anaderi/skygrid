package com.github.anaderi.skygrid.executor.wooster;

import junit.framework.TestCase;

import java.io.IOException;
import java.net.MalformedURLException;

/**
 * Created by stromsund on 22.02.15.
 */
public class RemoteQueueTest extends TestCase {
    public void testGetInfo() throws MalformedURLException, IOException {
        RemoteQueue q = new RemoteQueue("http://metascheduler.test.vs.os.yandex.net/", "stromsund-a");
        RemoteQueue.QueueInfo qi = q.getInfo();
        q.getTask();
        System.out.println(qi);
    }
}
