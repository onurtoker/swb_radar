import uhd
from uhd import libpyuhd as lib
import numpy as np
import scipy.io
import threading
import matplotlib.pyplot as plt
import time
from timeit import default_timer as timer

from myConstants import *
import myUSRP

# USRP selection
usrpTX = myUSRP.Device("serial=30B0CAB")
#usrpTX.usrp.set_clock_source('external')
usrpRX = myUSRP.Device("serial=30AD28B")
#usrpRX.usrp.set_clock_source('external')

fstart = 1.9e9
fstop  = 4.2e9
nfreq = 200

# Global variables for test/debug
mydata_x0 = np.empty((nfreq, ns * nrep), dtype=np.complex)
mydata_x1 = np.empty((nfreq, ns * nrep), dtype=np.complex)


# def reject_outliers(data, m=5):
#     return data[abs(data - np.mean(data)) < m * np.std(data)]


def start_experiment():
    # USRP initialization
    usrpTX.set_tx_config(fLO, fs, channelsTX, gainTX)
    usrpRX.set_rx_config(fLO, fs, channelsRX, gainRX)
    tx_buffer = 0.7*np.array([1 + 1j], dtype=np.complex64)
    usrpTX.start_tx_stream(tx_buffer)
    usrpRX.start_rx_stream()


def stop_experiment():
    usrpTX.stop_tx_stream()
    usrpRX.stop_rx_stream()


def measCFR(f,df):

    usrpRX.chg_rx_freq(f - df)
    usrpTX.chg_tx_freq(f)

    time.sleep(lo_settling_time)
    usrpRX.discard_rx_samples(nrep)

    meas_x0 = np.empty((nrep, ns), dtype=np.complex)
    meas_x1 = np.empty((nrep, ns), dtype=np.complex)

    for k in range(nrep):
        samps = usrpRX.get_rx_buffer()

        # Parse
        x0 = samps[0, :]
        x1 = samps[1, :]

        meas_x0[k,:] = x0
        meas_x1[k,:] = x1

    print('freq = {:5.2f} GHz'.format(f/1e9))
    return meas_x0, meas_x1


def genCFR(fstart, fstop, nfreq):

    start_experiment()
    print('System ready, start timer')
    start_time = timer()

    fvals = np.linspace(fstart, fstop, nfreq)
    for (k,f) in enumerate(fvals):
        meas_x0, meas_x1 = measCFR(f, fs/100)
        mydata_x0[k,:] = meas_x0.reshape((1,-1))
        mydata_x1[k,:] = meas_x1.reshape((1,-1))

    stop_experiment()
    print('Elapsed time = {:5.2f} sec'.format(timer() - start_time))

    data={}
    data['fvals'] = fvals
    data['mydata_x0'] = mydata_x0
    data['mydata_x1'] = mydata_x1
    scipy.io.savemat('results.mat', data)


if __name__ == "__main__":

    t = threading.Thread(target=genCFR, args=(fstart, fstop, nfreq))
    t.start()
    t.join()

    print('Measurement completed')

