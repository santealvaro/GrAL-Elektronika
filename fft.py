import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import heartpy as hp
import heartpy.filtering

# Cargar el archivo CSV
df = pd.read_csv("latido.csv")

# Definir nombres de las columnas
x_col = "timestamp"  # Tiempo en milisegundos
y_col = "signal"      # Señal del ECG

# Convertir tiempo de milisegundos a segundos
df[x_col] = (df[x_col] - df[x_col].min()) / 1000

# Calcular la frecuencia de muestreo (fs2)
fs2 = 1 / np.mean(np.diff(df[x_col]))


# Aplicar filtro pasa banda [1Hz - 30Hz]
df[y_col] = hp.filtering.filter_signal(data=df[y_col], cutoff=[1, 30], sample_rate=fs2, filtertype='bandpass')

# Extraer datos
t = df[x_col].values  # Tiempo en segundos
y = df[y_col].values  # Señal filtrada

# Calcular la Transformada de Fourier
N = len(y)  # Número de muestras
T = 1 / fs2  # Período de muestreo en segundos
yf = np.fft.fft(y)  # FFT de la señal
xf = np.fft.fftfreq(N, T)  # Frecuencias asociadas

# Tomar solo la mitad positiva del espectro
N_half = N // 2
xf = xf[:N_half]
yf = np.abs(yf[:N_half])  # Magnitud de la FFT

# Graficar la Transformada de Fourier (ECG)
plt.figure(figsize=(10,5))
plt.plot(xf, yf, color='b', linestyle='-')
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Amplitud")
plt.title("Transformada de Fourier de la Señal ECG")
plt.grid(True)
plt.xlim(0, 50)  # Limitar a frecuencias relevantes del ECG
plt.show()
