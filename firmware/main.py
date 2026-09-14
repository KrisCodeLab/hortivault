import time
import json
import sensor_manager
import gc

print("HortiVault – System bootet...")

gc.collect()

# Sensoreinstellungen laden und Sensoren initialisieren
active_sensors = sensor_manager.load_and_build()

print("\nAlle Sensoren initialisiert. Starte Messzyklus...\n")

# Sensormesswerte kontinuierlich auslesen und ausgeben
while True:
    sensor_data = {}
    
    for sensor_name, sensor_obj in active_sensors.items():
        try:
            data = sensor_obj.read()

            if data is not None:
                sensor_data[sensor_name] = data

        except Exception as e:
            print(f"[Fatal Error] Sensor '{sensor_name}' nicht erreichbar: {e}")
    
    if sensor_data:
        try:
            print(json.dumps(sensor_data))
            
        # Excpetion, falls der Server nicht erreichbar ist oder der Puffer blockiert ist
        except OSError as e:
            print(f"[OS Error] Konnte Paket nicht senden: {e}")
    else:
        print("[Warnung] Keine Sensoren aktiv oder erreichbar.")
        
    gc.collect()
    time.sleep(5)