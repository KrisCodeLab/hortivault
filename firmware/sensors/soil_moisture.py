import time
from machine import ADC, Pin

class SoilMoistureSensor:
    UNIT_MOIST = "percent"
    UNIT_RAW = "adc_raw"


    def __init__(self, adc_pin, air_value, water_value, test_mode):
        self.adc_pin = ADC(Pin(adc_pin))
        self.air_value = air_value
        self.water_value = water_value

        self.test_mode = test_mode
        self.test_counter = 0
        self.mock_is_dry = False

        self.adc_pin.atten(ADC.ATTN_11DB)


    def read(self):
        """Methode für main.py. Prüft ob Sensor im Test oder Livemodus läuft."""
        if self.test_mode:
            self.test_counter += 1
            return self._test_read(self.test_counter)
        return self._real_read()      
    

    def _real_read(self):
        # Korrekte Kalibrierung prüfen
        if self.air_value <= self.water_value:
                print("[Warnung] Soil Moisture Sensor ist noch nicht kalibriert!")
                return self._sensor_error()
        
        try:
            # Spannung am ADC Pin messen

            raw_moist = 0

            for _ in range(30):
                raw_moist += self.adc_pin.read()
                time.sleep_ms(10)

            raw_moist = raw_moist // 30

            # Meswert in Prozentangabe umrechnen
            moist = ((self.air_value - raw_moist) / (self.air_value - self.water_value)) * 100
            moist = max(0, min(100, moist))

            return { 
                "is_test": False,
                "real": {"moisture": {"value": round(moist, 1), "unit": self.UNIT_MOIST}},
                "raw": {"moisture": {"value": raw_moist, "unit": self.UNIT_RAW}}
            }
        
        except Exception as e:
            print(f"[Sensor Error] Soil Moisture Sensor: {e}")
            return self._sensor_error()


    def _test_read(self, counter):
        """Generiert Mock-Daten für die Bodenfeuchtigkeit (20-80%)."""

        if counter >= 100:
            self.mock_is_dry = not self.mock_is_dry  
            self.test_counter = 0                    
        
        if self.mock_is_dry:
            raw_moist = self.air_value  
        else:
            raw_moist = 0              

        moist = ((self.air_value - raw_moist) / (self.air_value - self.water_value)) * 100
        moist = max(0, min(100, moist))

        return { 
            "is_test": True,
            "real": {"moisture": {"value": round(moist, 1), "unit": self.UNIT_MOIST}},
            "raw": {"moisture": {"value": raw_moist, "unit": self.UNIT_RAW}}
            }
    

    def _sensor_error(self):
        return {
            "is_test": self.test_mode,
            "real": {"moisture": {"value": None, "unit": self.UNIT_MOIST}},
            "raw": {"moisture": {"value": None, "unit": self.UNIT_RAW}}
            }
