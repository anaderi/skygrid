package com.github.anaderi.skygrid.executor.wooster;

import com.github.anaderi.skygrid.executor.common.ExecutionTask;
import com.github.anaderi.skygrid.executor.common.JobDescriptor;
import com.sun.tools.javac.util.Convert;
import org.apache.commons.io.IOUtils;
import org.codehaus.jackson.map.DeserializationConfig;
import org.codehaus.jackson.map.ObjectMapper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;


public class RemoteQueue {
    public RemoteQueue(String host, String queue_name) throws MalformedURLException {
        StringBuilder management_url_builder_ = new StringBuilder();
        management_url_builder_.append(host);
        if (!host.endsWith("/"))
            management_url_builder_.append("/");
        management_url_builder_.append("queues");
        management_url_ = new URL(management_url_builder_.toString());
        StringBuilder url_builder_ = new StringBuilder(management_url_builder_.toString());
        url_builder_.append('/');
        url_builder_.append(queue_name);
        data_url_ = new URL(url_builder_.toString());
        info_url_ = new URL(url_builder_.toString() + "/info");
        mapper.configure(DeserializationConfig.Feature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    }

    public QueueInfo getInfo() throws IOException {
        HttpURLConnection connection = (HttpURLConnection)info_url_.openConnection();
        connection.setRequestMethod("GET");
        connection.connect();
        InputStream stream = connection.getInputStream();
        String json = IOUtils.toString(stream);
        connection.disconnect();
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(json, QueueInfo.class);
    }

    public boolean isEmpty() throws IOException {
        QueueInfo info = getInfo();
        return info.exists && info.length > 0;
    }

    public JobDescriptor getTask() throws IOException {
        if (!getInfo().exists)
            return null;
        HttpURLConnection connection = (HttpURLConnection)data_url_.openConnection();
        connection.setRequestMethod("GET");
        connection.connect();
        InputStream stream = connection.getInputStream();
        String json = IOUtils.toString(stream);
        JobDescriptor tmp_task = mapper.readValue(json, JobDescriptor.class);
        if (!tmp_task.success) {
            throw new IOException();
        }
        if (tmp_task.job == null)
            return null;
        return tmp_task;
    }

    private ObjectMapper mapper = new ObjectMapper();
    private URL management_url_;
    private URL info_url_;
    private URL data_url_;

    public static class QueueInfo {
        public boolean exists;
        public boolean success;
        public int length;
    }
}
