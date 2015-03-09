package com.github.anaderi.skygrid.executor.common;

/**
 * Created by stromsund on 03.03.15.
 */
public class JobDescriptor {
    public Boolean success;
    public Job job;

    public static class Job {
        public ExecutionTask descriptor;
        public String job_id;
        public String status;
    }

    public int hashCode() {
        if (job != null)
            return job.job_id.hashCode();
        return success.hashCode();
    }

    public boolean equals(Object o) {
        if (o instanceof JobDescriptor) {
            JobDescriptor other = (JobDescriptor)o;
            if (other.job != null && job != null) {
                return other.job.job_id.equals(job.job_id);
            } else if (other.job == null && job == null) {
                return other.success == success;
            }
        }
        return false;
    }
}
