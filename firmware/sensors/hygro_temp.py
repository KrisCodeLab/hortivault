import time
import random
from machine import I2C, Pin

class HygroTempSensor:
    # 1. HIER SIND DIE NEUEN PARAMETER IN DER __init__
    def __init__(self, i2c_bus, scl_pin, sda_pin, address, test_mode=False, temp_offset=0.0, hum_offset=0.0):
        self.test_mode = test_mode
        self.address = address
        
        self.i2c_bus = i2c_bus
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.i2c = None
        
        # 2. Wir speichern die Offsets im Objekt ab
        self.temp_offset = temp_offset
        self.hum_offset = hum_offset

    def read(self):
        """Die einzige Methode, die von der main.py aufgerufen wird."""
        if self.test_mode:
            return self._test_read()
        return self._real_read()

    def _real_read(self):
        """Liest den CHT832X über I2C aus."""
        if self.i2c is None:
            self.i2c = I2C(self.i2c_bus, scl=Pin(self.scl_pin), sda=Pin(self.sda_pin))
            time.sleep(0.1)
            
        try:
            self.i2c.writeto(self.address, bytes([0x24, 0x00]))
            time.sleep_ms(60)
            buf = self.i2c.readfrom(self.address, 6)
            
            temp_raw = (buf[0] << 8) | buf[1]
            humi_raw = (buf[3] << 8) | buf[4]
            
            temp = -45.0 + 175.0 * (temp_raw / 65535.0)
            hum = 100.0 * (humi_raw / 65535.0)
            
            # 3. HIER WERDEN DIE OFFSETS ANGEWENDET
            temp += self.temp_offset
            hum += self.hum_offset
            
            return {
                "temperature": round(temp, 1),
                "humidity": round(hum, 1)
            }
            
        except Exception as e:
            print(f"[Sensor Error] HygroTemp: {e}")
            return {"temperature": None, "humidity": None}

    def _test_read(self):
        """Generiert Mock-Daten für die Schulentwicklung."""
        temp = round(random.uniform(18.0, 26.0), 1)
        hum = round(random.uniform(50.0, 75.0), 1)
        
        # 4. Offsets auch im Test-Modus anwenden für gleiches Verhalten
        temp += self.temp_offset
        hum += self.hum_offset
        
        return {
            "temperature": round(temp, 1),
            "humidity": round(hum, 1)
        }
    