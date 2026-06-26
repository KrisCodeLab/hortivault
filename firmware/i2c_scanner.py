from machine import Pin, SoftI2C
import time

print("Starte I2C Scan auf SCL=22, SDA=23...")
try:
    # Frequenz niedrig halten (10000), falls das 1.5m Kabel stört!
    i2c = SoftI2C(scl=Pin(22, Pin.PULL_UP), sda=Pin(23, Pin.PULL_UP), freq=10000)
    devices = i2c.scan()
    
    if devices:
        for d in devices:
            print(f"Sensor antwortet auf Adresse: {d} (Hex: {hex(d)})")
    else:
        print("-> Nichts gefunden. Bitte Kabel auf Pin 22 und 23 prüfen!")
except Exception as e:
    print(f"-> Fehler: {e}")