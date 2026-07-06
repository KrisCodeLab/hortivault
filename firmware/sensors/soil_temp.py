import time
import random
import machine
import onewire
import ds18x20

class SoilTempSensor:
    TEMP_UNIT = "celsius"
    RAW_UNIT = "raw_ds"


    def __init__(self, ds_pin, test_mode, temp_offset=0.0):    
        self.ds_pin = machine.Pin(ds_pin)
        self.ow_bus = onewire.OneWire(self.ds_pin)
        self.ds_sensor = ds18x20.DS18X20(self.ow_bus)

        self.test_mode = test_mode
        self.temp_offset = temp_offset
        
        try:
            self.roms = self.ds_sensor.scan()
        except Exception:
            self.roms = []


    def read(self):
        """Methode für main.py. Prüft ob Sensor im Test oder Livemodus läuft."""
        if self.test_mode:
            return self._test_read()
        return self._real_read()


    def _real_read(self):
        """Liest den Sensor über das 1-Wire Protokoll aus."""
        if not self.roms:
            try:
                self.roms = self.ds_sensor.scan()
            except Exception:
                pass 

        if not self.roms:
            print("[Sensor Error] SoilTemp: Kein Sensor an diesem Pin gefunden!")
            return self._sensor_error()
            
        try:
            self.ds_sensor.convert_temp()
        
            time.sleep_ms(750) 
            
            temp = self.ds_sensor.read_temp(self.roms[0])
            temp += self.temp_offset
            
            return {
                "is_test": False,
                "real": {"temperature": {"value": round(temp, 1), "unit": self.TEMP_UNIT}},
                "raw": {"temperature": {"value": int(temp * 16), "unit": self.RAW_UNIT}}
            }
            
        except Exception:
            print(f"[Sensor Error] SoilTemp: Kein Sensor an diesem Pin gefunden!")
            return self._sensor_error()


    def _test_read(self):
        """Generiert Mock-Daten, wenn TEST_MODE in der config.py auf True steht."""
        temp = round(random.uniform(18.0, 22.0), 1)
        temp += self.temp_offset
        
        return {
            "is_test": True,
            "real": {"temperature": {"value": round(temp, 1), "unit": self.TEMP_UNIT}},
            "raw": {"temperature": {"value": int(temp * 16), "unit": self.RAW_UNIT}}
        }
    

    def _sensor_error(self):
        return {
            "is_test": self.test_mode,
            "real": {"temperature": {"value": None, "unit": self.TEMP_UNIT}},
            "raw": {"temperature": {"value": None, "unit": self.RAW_UNIT}}
        }