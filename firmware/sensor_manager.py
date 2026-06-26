import config
from sensors import HygroTempSensor

# Registry mit allen bekannten Sensor-Klassen
SENSOR_REGISTRY = {
    "HygroTempSensor": {
        "class": HygroTempSensor, 
        "allowed_args": ["temp_offset", "hum_offset", "test_mode"]
    }
}


def build_sensors(settings_json):
    """Baut Sensor-Objekte basierend auf den Benutzereinstellungen und der config.py."""
    active_sensors = {}
    used_pins = [] 
    
    for sensor_name, user_config in settings_json.get("sensors", {}).items():
        sensor_type = user_config.get("type")
        
        # Check ob Sensortyp bekannt ist
        if sensor_type not in SENSOR_REGISTRY:
            print(f"[Fehler] Unbekannter Sensortyp '{sensor_type}'.")
            continue
            
        SensorClass = SENSOR_REGISTRY[sensor_type]["class"]
        allowed_args = SENSOR_REGISTRY[sensor_type]["allowed_args"]
        
        # Alle Verfügbaren Hardware-Ports für diesen Sensortyp abrufen
        available_pins = config.HARDWARE_PINS.get(sensor_type, [])
        assigned_pins = None
        
        # Freien Pin suchen und belegen
        for pin in available_pins:
            if pin not in used_pins:
                assigned_pins = pin
                used_pins.append(pin) 
                break
                
        if not assigned_pins:
            print(f"[Fehler] Kein freier Steckplatz mehr für '{sensor_name}' ({sensor_type}) verfügbar!")
            continue
            
        # Sensor Parameter zusammenstellen
        kwargs : dict[str, object] = {
        #    "test_mode": config.TEST_MODE,
        }

        kwargs.update(assigned_pins) # Die ermittelten Pins hinzufügen
        
        # Nur die erlaubten Argumente aus der Benutzereingabe übernehmen
        for arg in allowed_args:
            if arg in user_config:
                kwargs[arg] = user_config[arg]
        
        # Sensor-Objekt instanziieren und in active_sensors speichern
        try:
            sensor_object = SensorClass(**kwargs)
            active_sensors[sensor_name] = sensor_object
            print(f"[Erfolg] '{sensor_name}' automatisch zugewiesen an: {assigned_pins}")
            
        except Exception as e:
            print(f"[Fehler] Konnte '{sensor_name}' nicht starten: {e}")
            
    return active_sensors