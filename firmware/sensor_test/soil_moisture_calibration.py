from machine import ADC, Pin
import time

adc_pin = ADC(Pin(32))
adc_pin.atten(ADC.ATTN_11DB)

print("Starte Kalibrierung...")

raw_moist = 0

for _ in range(1000):
    raw_moist += adc_pin.read()
    time.sleep(0.01)

raw_moist = raw_moist // 1000
print(f"Kalibrierung beendet. Rohwert: {raw_moist}")