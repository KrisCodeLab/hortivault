import time
import json
import sensor_manager

print("hortivault – System bootet...")

# sensor_settings laden
try:
    with open('sensor_settings.json', 'r') as file:
        settings = json.load(file)
except Exception as e:
    print(f"Hinweis: 'sensor_settings.json' nicht gefunden oder leer. ({e})")
    settings = {"sensors": {}}

# Sensoren über den Manager instanziieren
active_sensors = sensor_manager.build_sensors(settings)

print("\nAlle Sensoren initialisiert. Starte Messzyklus...\n")

# Sensormesswerte kontinuierlich auslesen und ausgeben
while True:
    payload = {}
    
    for sensor_name, sensor_obj in active_sensors.items():
        try:
            payload[sensor_name] = sensor_obj.read()
        except Exception as e:
            payload[sensor_name] = {"error": str(e)}
    
    if payload:
        print(json.dumps(payload))
    else:
        print("[Warnung] Keine Sensoren aktiv.")
        
    time.sleep(5)