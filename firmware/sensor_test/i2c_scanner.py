from machine import SoftI2C, Pin

# Eingestellten Pins eintragen
scl_pin = 4
sda_pin = 2

i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=10000)

print("Scanne I2C Bus...")
devices = i2c.scan()

if len(devices) == 0:
    print("Kein Sensor gefunden! (Hardware/Kabel-Problem)")
else:
    print("Geräte gefunden unter Adresse(n):")
    for device in devices:
        print(f"- Hex: {hex(device)}")