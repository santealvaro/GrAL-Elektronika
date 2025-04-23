###################################################################
#
#    Este fichero se ha creado para obtener los datos de ECG
#    de la base de datos y utilizarlos para crear gráficas y
#    generar los ficheros .csv
#
#    La base de datos utilizada se ha obtenido de Physionet:
#    https://physionet.org/content/szdb/1.0.0/
#
###################################################################

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
    folder = 'szdb/'

    record = wfdb.rdrecord(record_name = folder + rec_name, sampfrom = sfrom, sampto = sto)

    signal = record.p_signal
    time = []
    for i in range(0, sto - sfrom): time.append(i / fs)
    
    # heartpy elimina el offset de la señal, así que lo añadimos (para graficar únicamente)
    if (n == '6'): offset = 2.7
    else: offset = 1.05

    filtered = heartpy.filtering.filter_signal(data = signal[:,0], cutoff = [1, 30], sample_rate = fs, filtertype = 'bandpass') + offset
    
    plt.plot(time,signal,'b',label='Señal de ECG sin filtrar')
    plt.plot(time,filtered,'r',label='Señal filtrada')
    plt.xlabel("tiempo (s)")
    plt.ylabel("Señal de ECG (mV)")
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

def samp2t(samp, fs = 200):
    t = samp / fs
    return int(t)

def timeFormat(t, fs=200):
    
    horas = int(t // 3600)
    minutos = int((t % 3600) // 60)
    segundos = int(t % 60)

    # Formatear como h:m:s
    return f"{horas:02}_{minutos:02}_{segundos:02}"
def mean(list):
    suma = 0
    media = 0
    i = 0
    for element in list:
        suma += float(element)
        i += 1
    media = suma/i
    return media

def dataToCsv(n, sfrom, sto, is_sz, fileName):
    """
    Function used extract the data from the physionet database ECGs and convert it to csv
    Arguments:
        n: number of the sample
        sfrom: starting sample
        sto: ending sample
        is_sz: if the ECG contains data from a seizure 1
            if not 0
        fileName: name of the file where the information will be stored
        tempEnd: variable used to link the 
    Returns:
        ECGData: csv file with the data from the ECG within the given samples with
        "time[ms], ECG_value[mV], heart_rate[bpm], iz_sz" format
    """
    fs = 200 #according to the database, this is the sampling time
    rec_name = 'sz0' + str(n)
    folder = 'szdb/'
    
    # Leemos la grabacion y obtenemos la señal física (en mV)
    record = wfdb.rdrecord(record_name=folder+rec_name,sampfrom=sfrom,sampto=sto)
    s_fisica = record.p_signal[:,0]
    # Recogemos en una lista el número de muestras de cada intervalo R-R
    rr_samples = processing.ann2rr(record_name=folder+rec_name,extension='ari')
    rr_samples = rr_samples.tolist()
    # Filtramos la señal
    #signal = heartpy.filtering.filter_signal(data=s_fisica, cutoff= 50, sample_rate=fs, filtertype='notch')
    signal = heartpy.filtering.filter_signal(data=s_fisica, cutoff= [1,30], sample_rate=fs, filtertype='bandpass')
    

    # Queremos una lista de dimensión 1x(sto-sfrom) que contenga el ritmo cardiaco de cada muestra
    RR_interval = []
    n_samp = 0
    for j in range(0,len(rr_samples)):
        rr_val = rr_samples[j]
        n_samp+=rr_val
        if (n_samp >= sfrom and n_samp <= sto):
            for i in range(0,rr_val): RR_interval.append(fs*60/rr_val) # [bpm]

    # RR_interval puede que no coincida exactamente con la longitud de signal
    # por errores en la medida o en las anotaciones => modificamos len(RR_interval)
    dif = len(signal)-len(RR_interval)
    meanBPM = mean(RR_interval)
    if (dif>0):
        for i in range(0,dif): RR_interval.append(meanBPM)
    elif (dif<0):  RR_interval = RR_interval[:dif]

    # Obetnemos las listas de tiempo y convulsion, de la misma dimensión que signal
    t_array = []
    time = samp2t(sfrom) * 1000
    sz_array = []
    for i in range(0,sto-sfrom):
        t_array.append(time)
        time += 5 # sumamos 5 milisegundos
        sz_array.append(is_sz)
    
    data = {'timestamp':t_array,'signal':signal,'heart_rate':RR_interval,'seizure':sz_array}
    df = pd.DataFrame(data=data)
    df.to_csv('samples/'+fileName+'.csv',index=False)
    

beginning = t2samp('01:08:02')
end = t2samp('01:09:32')
tempBeginning = beginning
fs = 200
while tempBeginning < end:
    tempEnd = tempBeginning + 30 * fs
    t = samp2t(tempBeginning)
    hMinSec = timeFormat(t)
    dataToCsv('7', tempBeginning, tempEnd, 1, 'sz07_' + hMinSec + "seizure")
    tempBeginning = tempEnd

#df = pd.read_csv("ecgDataReduced.csv")
#tiempo = df["timestamp"]
#fs2 = 2 / (0.012 + 0.011)
#signal = heartpy.filtering.filter_signal(data=df["signal"], cutoff= [1,30], sample_rate=fs2, filtertype='bandpass')
#plt.plot(df["timestamp"], signal)
#plt.plot(df["timestamp"], df["signal"])
#plt.show()
