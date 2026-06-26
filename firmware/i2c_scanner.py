from machine import Pin, SoftI2C

print("Starte I2C Scan auf SCL=22, SDA=23...")
try:
    i2c = SoftI2C(scl=Pin(22, Pin.PULL_UP), sda=Pin(23, Pin.PULL_UP), freq=10000)
    devices = i2c.scan()
    
    if devices:
        for d in devices:
            print(f"Sensor antwortet auf Adresse: {d} (Hex: {hex(d)})")
    else:
        print("-> Keine Sensoren gefunden.")
except Exception as e:
    print(f"-> Fehler: {e}")