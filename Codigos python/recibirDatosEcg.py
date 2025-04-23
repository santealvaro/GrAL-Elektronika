import paho.mqtt.client as mqtt
import csv

# Configuración MQTT
mqtt_server = "192.168.1.40"  # IP del broker MQTT
mqtt_port = 1883             # Puerto MQTT
topicECG = "ECG/data"        # Tópico donde se reciben los datos

# Archivo CSV donde se guardarán los datos
csv_file = "prueba.csv"

# Callback cuando el cliente recibe un mensaje
def on_message(client, userdata, msg):
    print(f"Mensaje recibido: {msg.payload.decode('utf-8')}")  #Mensaje recibido
    # Decodificar el mensaje recibido
    message = msg.payload.decode('utf-8')
    
    # Separar el mensaje en los pares de datos por coma
    data = message.strip(',').split(',')
    
    # Asegurarnos de que los datos tengan un número par de elementos (tiempo y ECG)
    if len(data) % 2 == 0:
        # Procesar cada par de valores de tiempo y ECG
        for i in range(0, len(data), 2):
            timestamp = int(data[i])     # Tiempo
            signal = int(data[i + 1]) # Valor del ECG
            
            # Guardar los datos en el archivo CSV
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, signal])
                print(f"Datos guardados: {timestamp}, {signal}")  # Confirmación de guardado
    else:
        print("Datos no válidos recibidos.")  # Si el formato no es correcto

# Callback cuando el cliente se conecta al broker
def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código: {rc}")
    if rc == 0:
        client.subscribe(topicECG)
    else:
        print("Error al conectar al broker MQTT")

# Crear cliente MQTT
client = mqtt.Client()

# Asignar las funciones de callback
client.on_message = on_message
client.on_connect = on_connect

# Conectar al broker MQTT
print("Conectando al broker MQTT...")
client.connect(mqtt_server, mqtt_port, 60)

# Abrir el archivo CSV y escribir los encabezados (solo la primera vez)
try:
    with open(csv_file, mode='x', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "signal"])
except FileExistsError:
    pass  # El archivo ya existe, no hacemos nada

# Iniciar el bucle de MQTT para recibir los mensajes
print("Esperando mensajes MQTT...")
client.loop_forever()
