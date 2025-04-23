import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Parámetros
input_csv = '../samplesSensor/reposoAbsoluto.csv'       # Nombre del archivo de entrada
output_csv = '../samplesSensor/reposoRuido.csv'  # Nombre del archivo de salida
noise_std = 30

# Cargar el CSV
df = pd.read_csv(input_csv)

# Verifica que las columnas necesarias existen
if 'timestamp' not in df.columns or 'signal' not in df.columns:
    raise ValueError("El archivo CSV debe tener columnas 'timestamp' y 'signal'.")

# Añadir ruido gaussiano
np.random.seed(42)  # Para resultados reproducibles
noise = np.random.normal(0, noise_std, size=len(df))
df['signal_noisy'] = df['signal'] + noise

# Guardar el nuevo CSV
df.to_csv(output_csv, index=False)

plt.figure(figsize=(12, 6))
#plt.plot(df['timestamp'], df['signal'], label='Original', alpha=0.7)
plt.plot(df['timestamp'], df['signal_noisy'])
plt.xlabel('t (s)')
plt.ylabel('EKGaren balioa')
plt.title('Elektrokardiograma denboran zehar (normalizatuta)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
