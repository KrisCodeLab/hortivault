# ==========================================
# HortiVault - ESP32 Configuration
# ==========================================

# --- HARDWARE PINS ---
HARDWARE_PINS = {
    "HygroTempSensor": [
        {"i2c_bus": 0, "scl_pin": 22, "sda_pin": 23, "address": 0x44}
    ],

    "SoilTempSensor": [
        {"ds_pin": 15}
    ],

    "LightSensor": [
        {"i2c_bus": 0, "scl_pin": 4, "sda_pin": 2, "address": 0x23}
    ],

    "SoilMoistureSensor": [
        {"adc_pin": 32}
    ]
}

# --- NETZWERK ---
WIFI_SSID = "WLAN_Name"
WIFI_PASS = "WLAN_Passwort"
BACKEND_URL = "BACKEND_URL"