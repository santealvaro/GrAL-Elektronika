import pandas as pd
import matplotlib.pyplot as plt
import heartpy as hp
import heartpy.filtering
import numpy as np

# Ruta pdel archivo CSV

def normalizeToPhysionet(df):
    # Normalizar la columna 'signal' al rango [-0.2, 1.2]
    df["signal"] = -0.2 + (df["signal"] - 260) * 1.7 / 365
    return df

csv_file = "../samplesSensor/convulsion.csv"
#csv_file = "ecgData2.csv"

# Leer los datos desde el archivo CSV
df = pd.read_csv(csv_file)

# Asegurarse de que los datos están ordenados por tiempo
df = df.sort_values(by="timestamp")

#print(len(df["signal"]))
numPaq = len(df["signal"]) // 20

#df = df.iloc[:149 * 20]
#differences = np.diff(df["timestamp"]).astype('timedelta64[s]')

# Calcular la media de los intervalos de tiempo

#filtered_differences = differences[differences > 10]

#maximo = np.max(differences)
#minimo = np.min(filtered_differences)
#batez = np.mean(filtered_differences)
#print(numPaq)
#print(batez)
#print(maximo)
#print(minimo)
df = normalizeToPhysionet(df)

# Filtrar los datos de los primeros 10 segundos
start_time = df["timestamp"].iloc[0] 
end_time = start_time + 10 * 1000  # 10 segundos en milisegundos

# Filtrar las filas dentro del rango de 10 segundos
df_filtered = df[(df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)].copy()    

# Filtrar la señal ECG
toFilter = df_filtered["signal"].to_numpy()  # Convertir a array para heartpy
fs = 200  # Frecuencia de muestreo en Hz 


filtered = hp.filtering.filter_signal(toFilter, cutoff = [1, 30], sample_rate=fs, filtertype='bandpass')

# Normalizar las señales
df_filtered["ecg_value_normalized"] = (df_filtered["signal"] - df_filtered["signal"].min()) / (df_filtered["signal"].max() - df_filtered["signal"].min())
df_filtered["ecg_value_filtered_normalized"] = (filtered - filtered.min()) / (filtered.max() - filtered.min())

# Graficar ambas señales normalizadas en el mismo gráfico
plt.figure(figsize=(12, 6))
plt.plot((df_filtered["timestamp"] - start_time) / 1000, df_filtered["signal"], color="b")
#plt.plot((df_filtered["timestamp"] - start_time) / 1000, filtered, label="ECG filtrado", color="red")

# Título y etiquetas
plt.title("Elektrokardiograma denboran zehar (normalizatuta)")
plt.xlabel("t (s)")
plt.ylabel("EKGaren balioa")
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()
