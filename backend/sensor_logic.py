import math


def ppfd_converter(lux, conv_factor=0.02):
    """
    Wandelt einen Lux-Wert mit dem Umrechnungsfaktor 
    in einen PPFD (photosynthetische Photonenflussdichte) Wert in  μmol/m²/s um.
    """
    if lux is None:
        return None
    else:
        ppfd = round(lux * conv_factor)
        return ppfd


def vpd_converter(air_temp, rh, leaf_offset=2.0):
    """
    Berechnet das Dampfdruckdefizit (VPD) in kPa.
    0.61078 kPa = Sättigungsdampfdruck von Wasser bei 0 °C
    17.27 und 237.3 = Näherungsfaktor an die Clausius-Clapeyron-Gleichung
    """
    if air_temp is None or rh is None:
        return None
    else: 
        # Sättigungsdampfdruck am Blatt in kPa
        vp_leaf = 0.61078 * math.exp((17.27 * (air_temp - leaf_offset)) / ((air_temp - leaf_offset) + 237.3)) 
        # Sättigungsdampfdruck der Umgebungsluft in kPa
        vp_air = 0.61078 * math.exp((17.27 * air_temp) / (air_temp + 237.3))
        # Aktueller Dampfdruck der Luft in kPa
        avp_air = vp_air * (rh / 100.0)
        # Der VPD ist die Differenz zwischen dem Potenzial am Blatt und der Luft
        vpd = vp_leaf - avp_air
        return round(vpd, 2)


def data_converter(sensor_data):
    """
    konvertiert den VPD und PPFD Wert mit Hilfe der entsprechenden Funktionen 
    und fügt diese an die bestehende JSON an
    """
    for data in sensor_data.values():
        real_data = data["real"]

        if "humidity" in real_data and "temperature" in real_data:
            air_hum = real_data["humidity"]["value"]
            air_temp = real_data["temperature"]["value"]

            vpd = vpd_converter(air_temp=air_temp, rh=air_hum)
            data["real"]["vpd"] = {"value": vpd, "unit": "kPa"}
        
        if "light" in real_data:
            lux = real_data["light"]["value"]

            ppfd = ppfd_converter(lux)
            data["real"]["ppfd"] = {"value": ppfd, "unit": "μmol/m²/s"}

    return sensor_data


def event_warning(processed_data, sensor_configs):
    """generische Funktion um Events anhand voreingestellter min und max Werte zu triggern"""
    events = []

    for data_pack in processed_data:
        sensor_name = data_pack["sensor_name"]
        measurements = data_pack["measurements"]["real"]

        for measurement, value_dict in measurements.items():
            if measurement == "light":
                continue
            if value_dict["value"] is None:
                print(f"Keine Messwerte für Sensor: {sensor_name} verfügbar.")
                continue
            try:
                limit_min = sensor_configs[sensor_name][measurement]["min"]
                limit_max = sensor_configs[sensor_name][measurement]["max"]

                if value_dict["value"] < limit_min:
                    event_warning = "event_low"
                    limit = limit_min
                elif value_dict["value"] > limit_max:
                    event_warning = "event_max"
                    limit = limit_max
                else:
                    event_warning = "event_ok"
                    limit = None

                event_pack = {
                    "sensor_name": sensor_name,
                    "measurement": measurement,
                    "value": value_dict["value"],
                    "limit": limit,
                    "event": event_warning
                }

                events.append(event_pack)

            except Exception:
                # Print wird im Live Betrieb entfernt!
                print(f"[SYSTEM]: keine Limits definiert für Sensor: {sensor_name} / {measurement}")
                continue

    print(f"Folgende Events wurden getriggert:\n{events}")
    return events


def water_level_warning(waterlevel):
    """
    Prüft anhand des Boolean-Werts des Wasserstandsensors ob der Tank voll oder leer ist 
    und gibt eine entsprechende Warnung aus
    """
    if waterlevel is None:
        return "Wasserstand unbekannt! Bitte Sensoren prüfen!"
    elif not waterlevel:
        return "Wassertank leer, bitte auffüllen!"
    

########## Nachfolgende Funktionen wurden durch def event_warning() ersetzt! ##########

"""
def vpd_warning(vpd, vpd_min, vpd_max):
    if vpd is None:
        return "Aktueller VPD Wert unbekannt! Bitte Sensoren prüfen!"
    elif vpd < vpd_min:
        return f"VPD Wert zu gering! VPD: {vpd}kPa"
    elif vpd > vpd_max:
        return f"VPD Wert zu hoch! VPD: {vpd}kPa"


def soil_moist_warning(soil_moisture, moist_min, moist_max):
    "
    Prüft anhand des Bodenfeuchtewerts ob der Boden zu nass oder zu trocken ist 
    und gibt eine entsprechende Warnung aus
    "
    if soil_moisture is None:
        return "Aktueller Bodenfeuchte Wert unbekannt! Bitte Sensoren prüfen!"
    elif soil_moisture < moist_min:
        return f"Erde zu trocken! Sättigungsgrad: {soil_moisture}%"
    elif soil_moisture > moist_max:
        return f"Erde zu nass! Sättigungsgrad: {soil_moisture}%"
      

def soil_temp_warning(soil_temp, soil_temp_min, soil_temp_max):
    "
    Prüft anhand der Bodentemperatur ob das Substrat zu warm oder zu kalt ist 
    und gibt eine entsprechende Warnung aus
    "
    if soil_temp is None:
        return "Aktuelle Bodentemperatur unbekannt! Bitte Sensoren prüfen!"
    elif soil_temp < soil_temp_min:
        return f"Substrat zu kalt! Temperatur: {soil_temp}°C"
    elif soil_temp > soil_temp_max:
        return f"Substrat zu warm! Temperatur: {soil_temp}°C"
        

def humidity_warning(rh, rh_min, rh_max):
    "
    Prüft anhand des RLF Wertes ob die Umgebung zu trocken oder zu feucht ist 
    und gibt eine entsprechende Warnung aus
    "
    if rh is None:
        return "Aktuelle RLF unbekannt! Bitte Sensoren prüfen!"
    elif rh < rh_min:
        return f"Relative Luftfeuchtigkeit zu gering! RLF: {rh}%"
    elif rh > rh_max:
        return f"Relative Luftfeuchtigkeit zu hoch! RLF: {rh}%"


def temp_warning(temp, temp_min, temp_max):
    "
    Prüft anhand der Umgebungstemperatur ob die Umgebung zu warm oder zu kalt ist 
    und gibt eine entsprechende Warnung aus
    "
    if temp is None:
        return "Aktuelle Umgebungstemperatur unbekannt! Bitte Sensoren prüfen!"
    elif temp < temp_min:
        return f"Umgebung zu kalt! Temperatur: {temp}°C"
    elif temp > temp_max:
        return f"Umgebung zu warm! Temperatur: {temp}°C"
"""