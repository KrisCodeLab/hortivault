import time
import json
import sensor_manager
import gc

print("HortiVault – System bootet...")

gc.collect()
MEASUREMENT_DATA_PREFIX = "MEASUREMENT|"

# Sensoreinstellungen laden und Sensoren initialisieren
active_sensors = sensor_manager.load_and_build()

print("\nAlle Sensoren initialisiert. Starte Messzyklus...\n")

# Sensormesswerte kontinuierlich auslesen und ausgeben
while True:
    sensor_data = {}
    
    for sensor_id, sensor_pack in active_sensors.items():
        try:
            data = sensor_pack["object"].read()

            if data is not None:
                sensor_data[sensor_id] = {
                "display_name": sensor_pack["display_name"],
                "measurements": data
            }

        except Exception as e:
            print(f"[Fatal Error] Sensor '{sensor_id}' nicht erreichbar: {e}")
    
    if sensor_data:
        try:
            print(MEASUREMENT_DATA_PREFIX + json.dumps(sensor_data))
            
        # Excpetion, falls der Server nicht erreichbar ist oder der Puffer blockiert ist
        except OSError as e:
            print(f"[OS Error] Konnte Paket nicht senden: {e}")
    else:
        print("[Warnung] Keine Sensoren aktiv oder erreichbar.")
        
    gc.collect()
    time.sleep(5)