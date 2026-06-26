import time
import random
import machine
import onewire
import ds18x20

class SoilTempSensor:


    def __init__(self, ds_pin, test_mode, temp_offset=0.0):
        self.test_mode = test_mode
        self.temp_offset = temp_offset
        
        self.ds_pin_obj = machine.Pin(ds_pin)
        self.ow_bus = onewire.OneWire(self.ds_pin_obj)
        self.ds_sensor = ds18x20.DS18X20(self.ow_bus)
        
        self.roms = self.ds_sensor.scan()


    def read(self):
        """Methode für main.py. Prüft ob Sensor im Test oder Livemodus läuft."""
        if self.test_mode:
            return self._test_read()
        return self._real_read()


    def _real_read(self):
        """Liest den DS18B20 über das 1-Wire Protokoll aus."""
        if not self.roms:
            print("[Sensor Error] SoilTemp: Kein Sensor an diesem Pin gefunden!")
            return {"temperature": None}
            
        try:
            self.ds_sensor.convert_temp()
        
            time.sleep_ms(750) 
            
            temp = self.ds_sensor.read_temp(self.roms[0])
            temp += self.temp_offset
            
            return {
                "temperature": round(temp, 1)
            }
            
        except Exception as e:
            print(f"[Sensor Error] SoilTemp: {e}")
            return {"temperature": None}


    def _test_read(self):
        """Generiert Mock-Daten, wenn TEST_MODE in der config.py auf True steht."""
        temp = round(random.uniform(18.0, 22.0), 1)
        temp += self.temp_offset
        
        return {
            "temperature": round(temp, 1)
        }