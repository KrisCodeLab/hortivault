import time
import random
from machine import SoftI2C, Pin

class LightSensor:
    UNIT_LIGHT = "lux"
    UNIT_RAW = "i2c_raw"

   
    def __init__(self, i2c_bus, scl_pin, sda_pin, address, test_mode):
        self.i2c_bus = i2c_bus
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.address = address
        self.test_mode = test_mode
        self.i2c = None


    def read(self):
        """Methode für main.py. Prüft ob Sensor im Test oder Livemodus läuft."""
        if self.test_mode:
            return self._test_read()
        return self._real_read()
    

    def _real_read(self):
        """Liest den Sensor über SoftI2C aus."""
        # SoftI2C-Schnittstelle initialisieren, falls None
        if self.i2c is None:
            self.i2c = SoftI2C(
                scl=Pin(self.scl_pin, Pin.PULL_UP), 
                sda=Pin(self.sda_pin, Pin.PULL_UP), 
                freq=10000
            )
            time.sleep(0.1)
        
        try:
            # Sensor anpingen, um Messung zu starten
            self.i2c.writeto(self.address, bytes([0x10]))
            time.sleep_ms(20)

            # 2 Bytes vom Sensor lesen (Messdaten abholen)
            buf = self.i2c.readfrom(self.address, 2)
            raw_lux = (buf[0] << 8) | buf[1]

            # Rohdaten in echte Werte umrechnen
            lux = raw_lux / 1.2

            return { 
                "is_test": False,
                "real": {"light": {"value": round(lux, 1), "unit": self.UNIT_LIGHT}},
                "raw": {"light": {"value": raw_lux, "unit": self.UNIT_RAW}}
            }
        
        except Exception as e:
            self.i2c = None
            print(f"[Sensor Error] Lightsensor: {e}")
            return self._sensor_error()


    def _test_read(self):
        """Generiert Mock-Daten für den Testmodus."""
        raw_lux = random.randint(100, 5000)
        lux = raw_lux / 1.2
        
        return { 
            "is_test": True,
            "real": {"light": {"value": round(lux, 1), "unit": self.UNIT_LIGHT}},
            "raw": {"light": {"value": raw_lux, "unit": self.UNIT_RAW}}
        }
    

    def _sensor_error(self):
        return { 
                "is_test": self.test_mode,
                "real": {"light": {"value": None, "unit": self.UNIT_LIGHT}},
                "raw": {"light": {"value": None, "unit": self.UNIT_RAW}}
        }
