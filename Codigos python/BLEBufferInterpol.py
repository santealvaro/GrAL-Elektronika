import asyncio
import csv
from bleak import BleakClient
import os
import numpy as np

# Dirección MAC del dispositivo BLE (reemplaza con la dirección de tu dispositivo)
device_address = "dc:54:75:ca:ef:a1"

# UUID del servicio y la característica (actualizados)
ECG_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
ECG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Archivo CSV para almacenar los datos
csv_file = 'ecgData.csv'
timems = 0

# Umbrales de los intervalos
THRESHOLD_R = (350, 600)   # Pico R
THRESHOLD_P_T = (350, 400) # Ondas P y T (intermedios)
THRESHOLD_S = (270, 350)   # Valle S
POINTS_MISSING = 3  # Puntos a interpolar en los 15 ms de pérdida

# Función para guardar datos en CSV
def save_to_csv(time_ms, ecg_value):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal"])
        writer.writerow([time_ms, ecg_value])

# Función para interpolar usando los últimos 3 puntos conocidos
def interpolate_lost_data(last_values):
    global timems

    if len(last_values) < 3:
        return  # No hay suficientes puntos para interpolar

    x_known = [timems - 15, timems - 10, timems - 5]  # Tiempos de los últimos 3 valores recibidos
    y_known = last_values[-3:]  # Últimos 3 valores de la señal

    x_interp = [timems, timems + 5, timems + 10]  # Tiempos de los puntos perdidos

    # Interpolación lineal
    y_interp = np.interp(x_interp, x_known, y_known)

    # Ajuste adicional para R y S
    if THRESHOLD_R[0] < y_known[-1] < THRESHOLD_R[1]:  # Si es un pico R, reducimos gradualmente
        y_interp = [max(THRESHOLD_R[0], val - 10) for val in y_interp]
    elif THRESHOLD_S[0] < y_known[-1] < THRESHOLD_S[1]:  # Si es un valle S, aumentamos gradualmente
        y_interp = [min(THRESHOLD_S[1], val + 10) for val in y_interp]

    # Guardar los valores interpolados
    for val in y_interp:
        save_to_csv(timems, val)
        timems += 5

# Procesamiento de datos recibidos
def process_data(data):
    global timems  
    values = []

    # Extraer valores de los datos recibidos
    for i in range(0, len(data), 2):  
        ecg_value = int.from_bytes(data[i:i+2], byteorder='little')
        values.append(ecg_value)

    # Guardar valores recibidos en CSV con timestamps correctos
    for val in values:
        save_to_csv(timems, val)
        timems += 5

    # Interpolación en los 15 ms de pérdida usando los últimos 3 valores buenos
    interpolate_lost_data(values[-3:])

# Función que se ejecuta cada vez que llega un nuevo paquete de datos
def on_data_received(sender: int, data: bytearray):
    # Procesar los datos recibidos
    process_data(data)

# Función principal para leer los datos BLE
async def run():
    try:
        async with BleakClient(device_address) as client:
            print(f"Conectado a {device_address}")

            # Obtener los servicios usando la propiedad `services`
            services = client.services
            print(f"Servicios disponibles:")

            # Imprimir detalles de los servicios disponibles
            for service in services:
                print(f"Servicio UUID: {service.uuid}")
                for characteristic in service.characteristics:
                    print(f"  Característica UUID: {characteristic.uuid}")

            # Buscar el servicio ECG
            for service in services:
                if service.uuid == ECG_SERVICE_UUID:
                    for characteristic in service.characteristics:
                        if characteristic.uuid == ECG_CHARACTERISTIC_UUID:
                            print(f"Esperando datos de ECG...")
                            await client.start_notify(characteristic, on_data_received)  # Activa las notificaciones BLE

            # Mantener la conexión abierta
            await asyncio.sleep(3600)  # 1 hora de lectura (ajustable)
    except Exception as e:
        print(f"Error: {e}")


# Ejecutar la función principal
asyncio.run(run())
