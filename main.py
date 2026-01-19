import sys
import os
import paho.mqtt.client as mqtt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QPushButton, QLabel, QHBoxLayout, QGraphicsItem,
                            QMessageBox)
from PyQt6.QtCore import QTimer, Qt, QElapsedTimer
from PyQt6.QtGui import QFont, QColor
import pyqtgraph as pg
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
import pywt
from scipy.signal import find_peaks
import requests

# Configuración MQTT
MQTT_BROKER = yourIP
MQTT_PORT = 1883
TOPIC = "ECG/data"

# Configuración ECG
FS = 200  # Frecuencia de muestreo en Hz
SAMPLES_PER_MSG = 60
INTERVAL_MS = 5  # 5ms entre muestras (200Hz)
BUFFER_SIZE = 1000  # 5 segundos de datos (1000 muestras)
UPDATE_INTERVAL_MS = 20  # Actualizar gráfico cada 20ms
PREDICTION_INTERVAL_MS = 5000  # Predicciones cada 5 segundos

model = load_model("modeloWavelet.h5")
scaler = joblib.load("scalerWavelet.pkl")

def resource_path(relative_path):
    """ Devuelve la ruta absoluta a un recurso, útil cuando se usa PyInstaller """
    try:
        base_path = sys._MEIPASS  # carpeta temporal de PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



class ECGMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Variables de datos
        self.time_values = np.arange(0, BUFFER_SIZE * INTERVAL_MS, INTERVAL_MS)
        self.ecg_buffer = np.zeros(BUFFER_SIZE)
        self.current_index = 0
        self.risk_count = 0
        self.last_prediction_time = QElapsedTimer()
        self.last_prediction_time.start()
        
        # Configuración de la ventana
        self.setWindowTitle("EKG monitorea <3")
        self.setGeometry(100, 100, 1200, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Configurar interfaz
        self.setup_ui()
        
        # Configuración MQTT
        self.setup_mqtt()
        
        # Temporizador principal
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(UPDATE_INTERVAL_MS)
    
    def setup_ui(self):
        """Configura todos los elementos de la interfaz"""
        self.setup_header_panel()
        self.setup_ecg_plot()
        self.setup_status_panel()
    
    def setup_header_panel(self):
        """Configura el panel superior con controles"""
        header_panel = QWidget()
        header_layout = QHBoxLayout(header_panel)
        
        title = QLabel("EKG monitorea")
        title.setFont(QFont("Calibri", 16, QFont.Weight.Bold))
        
        self.connect_button = QPushButton("Konektatu🔌")
        self.connect_button.clicked.connect(self.connect_mqtt)
        
        self.disconnect_button = QPushButton("Deskonektatu❌")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_mqtt)
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.connect_button)
        header_layout.addWidget(self.disconnect_button)
        self.main_layout.addWidget(header_panel)
    
    def setup_ecg_plot(self):
        """Configura el widget del gráfico ECG"""
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#f5f9fa')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Anplitudea')
        self.plot_widget.setLabel('bottom', 't (ms)')
        self.plot_widget.setYRange(-0.2, 1.5)
        self.plot_widget.setXRange(0, 5000)
        
        self.ecg_curve = self.plot_widget.plot(
            pen=pg.mkPen(color='#e74c3c', width=2),
            shadowPen=pg.mkPen('#c0392b', width=1, alpha=0.1)
        )
        self.ecg_curve.setCacheMode(QGraphicsItem.CacheMode.ItemCoordinateCache)
        
        self.main_layout.addWidget(self.plot_widget, 1)
    
    def setup_status_panel(self):
        """Configura el panel inferior con información"""
        status_panel = QWidget()
        status_layout = QHBoxLayout(status_panel)
        
        self.status_label = QLabel("Egoera: Deskonektatuta")
        self.prediction_label = QLabel("Iragarpena: 0%")
        self.risk_label = QLabel("Arriskua: 0%")
        self.risk_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.prediction_label)
        status_layout.addWidget(self.risk_label)
        self.main_layout.addWidget(status_panel)

    def setup_mqtt(self):
        """Configura el cliente MQTT"""
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False

    def send_telegram_alert(self):
        try:
            BOT_TOKEN = your_token
            CHAT_ID = yourID
            message = "‼️ *ERASO EPILEPTIKOA*\n\n %100eko arriskua detektatu da!"
    
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, data=payload)
        except Exception as e:
            print(f"❌ Error al enviar Telegram: {e}")
    
    def normalize_to_physionet(self, val):
        """Normaliza los valores al rango PhysioNet [-0.2, 1.2]"""
        return -0.2 + (val - 260) * 1.7 / 365
    
    def connect_mqtt(self):
        """Inicia la conexión MQTT"""
        if not self.connected:
            try:
                self.client.connect(MQTT_BROKER, MQTT_PORT)
                self.client.loop_start()
                self.status_label.setText("Egoera: Konektatuta")
                self.connect_button.setEnabled(False)
                self.disconnect_button.setEnabled(True)
            except Exception as e:
                self.status_label.setText(f"Errorea: {str(e)}")
    
    def disconnect_mqtt(self):
        """Finaliza la conexión MQTT"""
        if self.connected:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                self.connected = False
                self.status_label.setText("Egoera: Deskonektatuta")
                self.connect_button.setEnabled(True)
                self.disconnect_button.setEnabled(False)
                self.connect_button.setText("Konektatu🔌")
            except Exception as e:
                self.status_label.setText(f"Errorea deskonektatzean: {str(e)}")
    
    def on_connect(self, client, userdata, flags, rc, properties):
        """Callback cuando se conecta al broker"""
        if rc == 0:
            self.connected = True
            client.subscribe(TOPIC)
            self.status_label.setText("Egoera: Konentatuta ✓")
            self.connect_button.setText("🟢 Konektatuta")
        else:
            self.status_label.setText(f"Error conexión: {rc}")
            self.connect_button.setEnabled(True)
    
    def on_message(self, client, userdata, msg):
        """Procesa los mensajes MQTT"""
        try:
            payload_str = msg.payload.decode().strip()
            ecg_samples = payload_str.split(',')
            
            for sample_str in ecg_samples:
                try:
                    raw_value = float(sample_str)
                    normalized_value = self.normalize_to_physionet(raw_value)
                    self.ecg_buffer[self.current_index] = normalized_value
                    self.current_index = (self.current_index + 1) % BUFFER_SIZE
                except ValueError:
                    continue
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
    
    def update(self):
        """Actualización principal que se ejecuta cada 20ms"""
        self.update_plot()
        
        # Verificar si es tiempo de hacer predicción (cada 5 segundos)
        if self.last_prediction_time.elapsed() >= PREDICTION_INTERVAL_MS:
            self.run_predictions()
            self.last_prediction_time.restart()
    
    def update_plot(self):
        """Actualiza el gráfico con los datos más recientes"""
        if self.current_index > 0:
            plot_data = np.concatenate((
                self.ecg_buffer[self.current_index:],
                self.ecg_buffer[:self.current_index]
            ))
            self.ecg_curve.setData(self.time_values, plot_data)
    
    def run_predictions(self):
        if not self.connected or self.current_index == 0:
            return
    
        ecg_data = np.concatenate((
            self.ecg_buffer[self.current_index:],
            self.ecg_buffer[:self.current_index]
        ))
    
        df = pd.DataFrame({
            'timestamp': self.time_values,
            'signal': ecg_data
        })
    
        df = self.calculate_bpm(df)
        features = self.preprocess_data(df)
    
        try:
            X = scaler.transform(features)
            X = X.reshape(-1, X.shape[1], 1)
            y_pred = model.predict(X)[0][0]
            pred_percent = y_pred * 100
    
            if y_pred > 0.8:
                self.risk_count = min(3, self.risk_count + 1)
            else:
                self.risk_count = max(0, self.risk_count - 1)
    
            self.prediction_label.setText(f"Iragarpena: {pred_percent:.1f}%")
            self.risk_label.setText(f"Arriskua: {int(self.risk_count / 3 * 100)}%")
    
            if self.risk_count >= 2:
                self.risk_label.setStyleSheet("color: #e74c3c;")
            else:
                self.risk_label.setStyleSheet("color: #2ecc71;")
    
            # Alerta visual y correo
            if self.risk_count >= 3:

                self.send_telegram_alert()
                self.alert_shown = True
    
                alert = QMessageBox()
                alert.setWindowTitle("‼️ Arriskua")
                alert.setText("Arriskua %100ra, laguntza bilatu!")
                alert.setIcon(QMessageBox.Icon.Warning)
                alert.exec()
    
                
    
            elif self.risk_count < 3:
                self.alert_shown = False
    
        except Exception as e:
            print(f"Error en predicción: {e}")

    
    def calculate_bpm(self, df, col_tiempo='timestamp', col_senal='signal'):
        """Calcula los BPM basados en los picos del ECG"""
        df = df.sort_values(by=col_tiempo)
        senal = df[col_senal].values
        tiempo = df[col_tiempo].values
        
        picos, _ = find_peaks(senal, height=0.5, distance=100)
        df['heart_rate'] = np.nan
        
        bpm_values = []
        for i in range(1, len(picos)):
            t_diff = tiempo[picos[i]] - tiempo[picos[i-1]]
            if t_diff > 0:
                bpm = 60000 / t_diff
                bpm_values.append(bpm)
                df.loc[picos[i-1]:picos[i], 'heart_rate'] = bpm
        
        mean_bpm = np.nanmean(bpm_values) if bpm_values else np.nan
        df['heart_rate'] = df['heart_rate'].fillna(mean_bpm)
        
        return df
    
    def wavelet_transform(self, signal, wavelet='db4', level=4):
        """Aplica transformada wavelet a la señal"""
        coeffs = pywt.wavedec(signal, wavelet, level=level)
        return np.concatenate([c.flatten() for c in coeffs])
    
    def preprocess_data(self, df):
        """Preprocesa los datos para el modelo"""
        wavelet_features = self.wavelet_transform(df["signal"].values)
        hr_mean = np.mean(df["heart_rate"].values)
        hr_std = np.std(df["heart_rate"].values)
        return np.concatenate([wavelet_features, [hr_mean], [hr_std]]).reshape(1, -1)
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ECGMonitor()
    window.show()
    sys.exit(app.exec())

