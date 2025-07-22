import asyncio
import csv
import os
from bleak import BleakClient

device_address = "dc:54:75:ca:ef:a1"

# UUID del servicio y la característica
ECG_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
ECG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Archivo CSV para almacenar los datos
csv_file = 'ecgData1.csv'
timems = 0

# Función para guardar datos en CSV
def save_to_csv(time_ms, ecg_value):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal"])
        writer.writerow([time_ms, ecg_value])

# Procesar datos recibidos
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

# Callback para recibir datos de ECG
def on_data_received(sender, data):
    process_data(data)

# Función asíncrona principal
async def run():
    try:
        async with BleakClient(device_address) as client:
            print(f"Conectado a {device_address}")

            # Obtener servicios tras la conexión
            await client.get_services()
            print("Servicios disponibles:")

            # Imprimir detalles de los servicios disponibles
            for service in client.services:
                print(f"Servicio UUID: {service.uuid}")
                for characteristic in service.characteristics:
                    print(f"  Característica UUID: {characteristic.uuid}")

            # Buscar el servicio ECG
            ecg_characteristic = None
            for service in client.services:
                if service.uuid == ECG_SERVICE_UUID:
                    for characteristic in service.characteristics:
                        if characteristic.uuid == ECG_CHARACTERISTIC_UUID:
                            ecg_characteristic = characteristic
                            break

            if ecg_characteristic:
                print(f"Suscribiéndose a {ECG_CHARACTERISTIC_UUID}...")
                await client.start_notify(ECG_CHARACTERISTIC_UUID, on_data_received)
                print("Recepción de datos iniciada. Esperando datos...")

                # Mantener la conexión abierta
                while True:
                    await asyncio.sleep(1)  # Mantiene la ejecución indefinidamente
            else:
                print("Error: No se encontró la característica ECG.")

    except Exception as e:
        print(f"Error: {e}")

# Ejecutar la función principal en un bucle de eventos
if __name__ == "__main__":
    asyncio.run(run())
