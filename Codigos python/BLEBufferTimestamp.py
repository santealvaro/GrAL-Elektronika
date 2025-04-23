import asyncio
import csv
import os
from bleak import BleakClient

# Dirección MAC del dispositivo BLE (reemplaza con la dirección de tu dispositivo)
device_address = "dc:54:75:ca:ef:a1"

# UUID del servicio y la característica
ECG_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
ECG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Archivo CSV para almacenar los datos
csv_file = 'ecgDataBLEBuffer20_3enchufao.csv'

def save_to_csv(timestamp, ecg_value):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal"])
        writer.writerow([timestamp, ecg_value])

def process_data(data):
    for i in range(0, len(data), 6):
        timestamp = int.from_bytes(data[i:i+4], byteorder='little')
        ecg_value = int.from_bytes(data[i+4:i+6], byteorder='little')
        save_to_csv(timestamp, ecg_value)

def on_data_received(sender: int, data: bytearray):
    process_data(data)

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

asyncio.run(run())
