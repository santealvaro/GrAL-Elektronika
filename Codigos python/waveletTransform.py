import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot as plt

# Función para leer el archivo CSV y extraer la señal ECG
def read_ecg_csv(filename):
    df = pd.read_csv(filename)
    t = df["timestamp"].values
    ecg_signal = df["signal"].values
    return t, ecg_signal

# Función para calcular la transformada wavelet continua (CWT)
def compute_wavelet_transform(ecg_signal, sampling_rate):
    scales = np.arange(1, 128)
    #coefficients, frequencies = pywt.cwt(ecg_signal, scales, 'morl', 1.0 / sampling_rate) #'haar', 'db', 'sym', 'coif', 'bior', 'rbio', 'dmey', 'gaus', 'mexh', 'morl', 'cgau', 'shan', 'fbsp', 'cmor'
    coefficients, frequencies = pywt.cwt(ecg_signal, scales, 'morl', 1.0 / sampling_rate)
    return coefficients, frequencies

# Función para detectar picos en la señal ECG
def detect_peaks(ecg_signal, threshold=0.6):
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(ecg_signal, height=threshold)
    return peaks

# Función para visualizar la señal y su transformada wavelet con anotaciones
def plot_wavelet_transform(t, ecg_signal, coefficients, frequencies, peaks):
    plt.figure(figsize=(10, 6))
    
    # Gráfica de la señal ECG con picos anotados
    plt.subplot(2, 1, 1)
    plt.plot(t, ecg_signal, label='ECG Signal')
    plt.scatter(t[peaks], ecg_signal[peaks], color='red', label='Peaks', marker='o')
    plt.title("Señal de ECG con detección de picos")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.legend()
    
    # Gráfica de la transformada wavelet con frecuencias clave anotadas
    plt.subplot(2, 1, 2)
    plt.imshow(abs(coefficients), aspect='auto', extent=[t[0], t[-1], frequencies[-1], frequencies[0]], cmap='jet')
    plt.title("Transformada Wavelet de la señal de ECG")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Frecuencia (Hz)")
    plt.colorbar(label="Magnitud")
    
    # Anotaciones en frecuencias clave
    key_frequencies = [1, 5, 10, 20, 50]  # Hz
    for freq in key_frequencies:
        plt.axhline(y=freq, color='white', linestyle='--', alpha=0.6, label=f'{freq} Hz')
    
    plt.legend()
    plt.tight_layout()
    plt.show()

# Programa principal
if __name__ == "__main__":
    filename = "samples/sz02_01_03_00seizure.csv"  # Nombre del archivo CSV
    sampling_rate = 200  # Hz (ajustar según los datos reales)
    t, ecg_signal = read_ecg_csv(filename)
    #print(pywt.wavelist())
    coefficients, frequencies = compute_wavelet_transform(ecg_signal, sampling_rate)
    peaks = detect_peaks(ecg_signal)
    plot_wavelet_transform(t, ecg_signal, coefficients, frequencies, peaks)
