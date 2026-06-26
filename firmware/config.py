# ==========================================
# HortiVault - ESP32 Configuration
# ==========================================

# --- SYSTEM-MODUS ---
# True  = Simulation
# False = Live-Betrieb 
TEST_MODE = True  

# --- HARDWARE PINS ---
HARDWARE_PINS = {
    "HygroTempSensor": [
        {"i2c_bus": 0, "scl_pin": 22, "sda_pin": 21, "address": 0x44}
    ]
}

# --- NETZWERK ---
WIFI_SSID = "WLAN_Name"
WIFI_PASS = "WLAN_Passwort"
BACKEND_URL = "BACKEND_URL"