package com.github.anaderi.skygrid.executor.wooster;

import com.github.anaderi.skygrid.executor.common.JobDescriptor;

import java.util.ArrayList;

public class JobDescriptorProcessingQueue {
    public synchronized void  AppendJobDescriptor(JobDescriptor jobDescriptor) {
        registeredJobDescriptors_.add(jobDescriptor);
        upcomingJobDescriptors_.add(jobDescriptor);
    }

    public synchronized void MarkJobDescriptorAsCompleted(JobDescriptor jobDescriptor) {
        runningJobDescriptors_.remove(jobDescriptor);
        successfully_completed_tasks_ += 1;
    }

    public synchronized void MarkJobDescriptorAsFailed(JobDescriptor jobDescriptor) {
        runningJobDescriptors_.remove(jobDescriptor);
        upcomingJobDescriptors_.add(jobDescriptor);
    }

    public synchronized boolean HasUpcomingTasks() {
        return !upcomingJobDescriptors_.isEmpty();
    }

    public synchronized int UpcomingQueueSize() {
        return upcomingJobDescriptors_.size();
    }

    public synchronized boolean IsCompletedSuccsessfully() {
        return successfully_completed_tasks_ == registeredJobDescriptors_.size();
    }

    public synchronized JobDescriptor GetNextTask() {
        JobDescriptor result = upcomingJobDescriptors_.get(0);
        upcomingJobDescriptors_.remove(0);
        runningJobDescriptors_.add(result);
        return result;
    }

    private ArrayList<JobDescriptor> registeredJobDescriptors_ = new ArrayList<JobDescriptor>();
    private ArrayList<JobDescriptor> upcomingJobDescriptors_ = new ArrayList<JobDescriptor>();
    private ArrayList<JobDescriptor> runningJobDescriptors_ = new ArrayList<JobDescriptor>();
    private int successfully_completed_tasks_ = 0;
}
