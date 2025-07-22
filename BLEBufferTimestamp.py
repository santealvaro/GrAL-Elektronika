import asyncio
import csv
import os
from bleak import BleakClient

# MAC del dispositivo bluetooth
device_address = "dc:54:75:ca:ef:a1"

# UUID del servicio y la característica
ECG_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
ECG_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

csv_file = 'ecgDataBLEBuffer20_3.csv'

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

            services = client.services
            print(f"Servicios disponibles:")

            # mostrar los sevicios y caracteristicas
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

            # Mantener conexion abierta
            await asyncio.sleep(3600) 
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(run())
