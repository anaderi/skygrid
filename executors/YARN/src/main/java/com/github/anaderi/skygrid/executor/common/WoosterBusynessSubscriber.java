package com.github.anaderi.skygrid.executor.common;

import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 * Interface for communication between Wooster and Agatha.
 */
public interface WoosterBusynessSubscriber extends Remote {
    public void onWoosterBusy() throws RemoteException;
}
