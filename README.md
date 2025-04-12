# GrAL-Elektronika
In this repository you will find all the programs i have used during the development of my final degree project and also all the data I have used to train the machine learning models (The data comes from https://physionet.org/content/szdb/1.0.0/ but i have divided it in 30sec windows and extracted some features).
\\\\
For receiving the data from the Arduino we have these programs:\\\\
-BLEBufferTimestamp, which is used to receive data buffers containing the measuring of the sensor and the time it was measured throug bluetoth low energy.\\
-BLESignalOnly, which is the same as the previous, but instead of sending the time from the arduino, I apply 5ms difference between each measurement myself\\
-filtrado, used to filter the signal from de data-base with 2 different filters (Notch and Bandpass filters). Additionally, the bpm of each beat is calculated and all the information is put into a csv file. \\
-graficarDatosEcg is used to plot the data from the csv\\
-MQTTBufferTimestamp is the same as BLEBufferTimestamp but with MQTT\\
-MQTTSigalOnly, same as BLESignalOnly but with MQTT\\
-EntrenarModeloWavelet is used to train the model using the wavelet transform\\
-EntrenarModelofft is used to train the model using the fft transform. The code is the one I used in google colab so perhaps you should change the file addresses\\
-Aplicacion contains functions from all the previous programs and is used to create a graphical interface to detect real time seizures\\
