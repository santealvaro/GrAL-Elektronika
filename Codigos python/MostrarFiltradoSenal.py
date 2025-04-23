import wfdb
from wfdb import processing
import heartpy
import heartpy.filtering
import pandas as pd
import matplotlib.pyplot as plt

def plotdata(n, sfrom, sto):
    """
        Function used to plot the data from the physionet database ECGs
        Arguments:
            n: number of the sample
            sfrom: starting sample
            sto: ending sample
    """
    fs = 200 #according to the database, this is the sampling time
    rec_name = 'sz0' + str(n)
    folder = '../szdb/'

    record = wfdb.rdrecord(record_name = folder + rec_name, sampfrom = sfrom, sampto = sto)

    signal = record.p_signal
    time = []
    for i in range(0, sto - sfrom): time.append(i / fs)
    
    # heartpy elimina el offset de la señal, así que lo añadimos (para graficar únicamente)
    if (n == '6'): offset = 2.7
    else: offset = 1.05

    filtered = heartpy.filtering.filter_signal(data = signal[:,0], cutoff = [1, 30], sample_rate = fs, filtertype = 'bandpass') + offset
    #filtered = heartpy.filtering.filter_signal(data = signal[:,0], cutoff = 50, sample_rate = fs, filtertype = 'notch')
    #plt.plot(time,signal,color = 'orange',label = 'Iragazi gabeko EKG seinalea')
    plt.plot(time, filtered, color='blue', label='Iragazitako seinalea')
    plt.xlabel("Denbora (s)")
    plt.ylabel("EKG seinalea (mV)")
    plt.legend()
    plt.show()


def t2samp(time, fs = 200):
    """
    Function used to go from the format hours:minutes:seconds to the number of samples within that time
    Arguments:
        time: time in hours:minutes:seconds
    Returns:
        samples: number of samples in the given time
    """
    h, mins, s = time.split(":")
    samples = (int(h) * 3600 + int(mins) * 60 + int(s)) * fs
    return samples

n = 1
inicio = t2samp("00:00:30")
fin = t2samp("00:00:32")

plotdata(n, inicio, fin)
