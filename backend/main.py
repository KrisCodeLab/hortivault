import time
import config
import serial_listener as listener
import data_manager as manager
import sensor_logic as logic

USB_PORT = '/dev/ttyUSB0'
BAUD = 115200

DATABASE = ""
HOST = ""
PORT = 5432
USER = ""
PASSWORD = ""

serial_listener = listener.SerialListener(USB_PORT, BAUD)
serial_listener.start_listener_thread()

data_manager = manager.DataManager(DATABASE, HOST, PORT, USER, PASSWORD)

if __name__ == "__main__":

    try:
        while True:
            sensor_data = serial_listener.get_data()
            if sensor_data:
                data_manager.data_distributor(sensor_data)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Programm durch Benutzer beendet.")
