import time
import random
from machine import SoftI2C, Pin

class HygroTempSensor:
    UNIT_TEMP = "celsius"
    UNIT_HUM = "percent"
    UNIT_RAW = "i2c_raw"
   
   
    def __init__(self, i2c_bus, scl_pin, sda_pin, address, test_mode, temp_offset=0.0, hum_offset=0.0):
        self.i2c_bus = i2c_bus
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.address = address
        self.test_mode = test_mode
        self.temp_offset = temp_offset
        self.hum_offset = hum_offset
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
            self.i2c.writeto(self.address, bytes([0x24, 0x00]))
            time.sleep_ms(60)

            # 6 Bytes vom Sensor lesen (Messdaten abholen)
            buf = self.i2c.readfrom(self.address, 6)
            # Bytes 2 und 4 werden ignoriert (CRC-Bytes / Prüfsummen-Bytes)
            temp_raw = (buf[0] << 8) | buf[1]
            humi_raw = (buf[3] << 8) | buf[4]
            
            # Rohdaten in echte Werte umrechnen
            temp = -45.0 + 175.0 * (temp_raw / 65535.0)
            hum = 100.0 * (humi_raw / 65535.0)
            
            temp += self.temp_offset
            hum += self.hum_offset
            
            return {
                "is_test": False,

                "real": {
                    "temperature": {"value": round(temp, 1), "unit": self.UNIT_TEMP},
                    "humidity": {"value": round(hum, 1), "unit": self.UNIT_HUM}
                },

                "raw": {
                    "temperature": {"value": temp_raw, "unit": self.UNIT_RAW},
                    "humidity": {"value": humi_raw, "unit": self.UNIT_RAW}
                }
            }
            
        except Exception as e:
            self.i2c = None
            print(f"[Sensor Error] HygroTemp: {e}")
            return self._sensor_error()


    def _test_read(self):
        """Deinitialisiert die Sensorhardware und Generiert Mock-Daten, wenn TEST_MODE in config.py = True gesetzt ist."""
        if self.i2c is not None:
            self.i2c = None

        temp_raw = random.randint(20000, 40000)
        humi_raw = random.randint(30000, 50000)

        temp = -45.0 + 175.0 * (temp_raw / 65535.0)
        hum = 100.0 * (humi_raw / 65535.0)
        
        temp += self.temp_offset
        hum += self.hum_offset
        
        return {
            "is_test": True,

            "real": {
                "temperature": {"value": round(temp, 1), "unit": self.UNIT_TEMP},
                "humidity": {"value": round(hum, 1), "unit": self.UNIT_HUM}
            },

            "raw": {
                "temperature": {"value": temp_raw, "unit": self.UNIT_RAW},
                "humidity": {"value": humi_raw, "unit": self.UNIT_RAW}
            }
        }
    

    def _sensor_error(self):
        return {
            "is_test": self.test_mode,

            "real": {
                "temperature": {"value": None, "unit": self.UNIT_TEMP},
                "humidity": {"value": None, "unit": self.UNIT_HUM}
            },
            
            "raw": {
                "temperature": {"value": None, "unit": self.UNIT_RAW},
                "humidity": {"value": None, "unit": self.UNIT_RAW}
            }
        }
