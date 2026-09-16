import time
import config
import serial_listener as listener
import data_manager as manager
import sensor_logic as logic

serial_listener = listener.SerialListener(**config.SERIAL_READER)
serial_listener.start_listener_thread()

data_manager = manager.DataManager(**config.DB_LOGIN)

if __name__ == "__main__":

    try:
        while True:
            sensor_data = serial_listener.get_data()
            if sensor_data:
                sensor_data = logic.data_converter(sensor_data)
                processed_data = data_manager.data_distributor(sensor_data)
                
                events = logic.event_warning(processed_data, sensor_configs=config.SENSOR_CONFIGS)
                data_manager.event_distributor(events)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programm durch Benutzer beendet.")
