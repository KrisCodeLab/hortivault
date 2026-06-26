import time
import json
import sensor_manager

print("hortivault – System bootet...")

# Sensoreinstellungen laden und Sensoren initialisieren
active_sensors = sensor_manager.load_and_build()

print("\nAlle Sensoren initialisiert. Starte Messzyklus...\n")

# Sensormesswerte kontinuierlich auslesen und ausgeben
while True:
    sensor_data = {}
    
    for sensor_name, sensor_obj in active_sensors.items():
        try:
            sensor_data[sensor_name] = sensor_obj.read()
        except Exception as e:
            sensor_data[sensor_name] = {"error": str(e)}
    
    if sensor_data:
        print(json.dumps(sensor_data))
    else:
        print("[Warnung] Keine Sensoren aktiv.")
        
    time.sleep(5)