import paho.mqtt.client as mqtt
import csv

# Configuración MQTT
mqtt_server = "172.20.10.2"  # IP del broker mosquitto
mqtt_port = 1883             # Puerto MQTT
topicECG = "ECG/data"        
timestamp = 0

csv_file = "../samplesSensor/reposoAbsoluto2.csv"


def on_message(client, userdata, msg):
    global timestamp
    print(f"Buffer recibido: {msg.payload.decode('utf-8')}")  
    # Decodificar el mensaje recibido
    message = msg.payload.decode('utf-8')
    
    # Separar el mensaje
    data = message.strip(',').split(',')
    

    for i in range(0, len(data), 1):
        signal = int(data[i]) # Valor del ECG
        timestamp += 5
        # Guardar los datos en el archivo CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, signal])
            print(f"Datos guardados: {timestamp}, {signal}")  
            
def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código: {rc}")
    if rc == 0:
        client.subscribe(topicECG)
    else:
        print("Error al conectar al broker MQTT")


client = mqtt.Client()


client.on_message = on_message
client.on_connect = on_connect


print("Conectando al broker MQTT...")
client.connect(mqtt_server, mqtt_port, 60)

try:
    with open(csv_file, mode='x', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "signal"])
except FileExistsError:
    pass  # El archivo ya existe, no hacemos nada

# bucle mqtt
print("Esperando mensajes MQTT...")
client.loop_forever()
