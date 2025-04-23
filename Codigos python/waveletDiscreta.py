import pandas as pd
import numpy as np
import pywt
import matplotlib.pyplot as plt

# === Cargar datos ===
df = pd.read_csv('../samples/sz01_00_01_00.csv')
df = df.iloc[0:int(len(df)/16)]
#df = df.iloc[0:int(len(df)/8)]
# Convertir 'timestamp' a datetime y calcular tiempo en segundos
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['time_seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

# Extraer tiempo y señal
fs = 200  # Frecuencia de muestreo en Hz
time = df['time_seconds']
signal = df['signal']

# === Aplicar Transformada de Wavelet Discreta ===
wavelet = 'db4'  # Tipo de wavelet
level = 3  # Niveles de descomposición
coeffs = pywt.wavedec(signal, wavelet, level=level)

# Extraer coeficientes
cA3, cD3, cD2, cD1 = coeffs  # Aproximación y detalles

# === Calcular nuevo tiempo para cada nivel de la DWT ===
def get_time_reduced(original_time, new_length):
    """Escala el tiempo original a la nueva longitud de coeficientes"""
    return np.linspace(original_time.iloc[0], original_time.iloc[-1], new_length)

time_cA3 = get_time_reduced(time, len(cA3))
time_cD3 = get_time_reduced(time, len(cD3))
time_cD2 = get_time_reduced(time, len(cD2))
time_cD1 = get_time_reduced(time, len(cD1))

# === Graficar resultados ===
plt.figure(figsize=(12, 8))

plt.subplot(5, 1, 1)
plt.plot(time, signal, color='b')
plt.title('Señal Original')

plt.subplot(5, 1, 2)
plt.plot(time_cA3, cA3, color='g')
plt.title('Aproximación cA3')

plt.subplot(5, 1, 3)
plt.plot(time_cD3, cD3, color='r')
plt.title('Detalle cD3')

plt.subplot(5, 1, 4)
plt.plot(time_cD2, cD2, color='orange')
plt.title('Detalle cD2')

plt.subplot(5, 1, 5)
plt.plot(time_cD1, cD1, color='purple')
plt.title('Detalle cD1')

plt.tight_layout()
plt.show()
