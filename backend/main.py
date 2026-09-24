import time
import config
import serial_listener as listener
import data_manager as manager
import sensor_logic as logic
import api

serial_listener = listener.SerialListener(**config.SERIAL_READER)
data_manager = manager.DataManager(**config.DB_LOGIN)
frontend_api = api.FrontendApi(**config.FRONTEND_API)

serial_listener.start_listener_thread()
frontend_api.start_api_thread()

api_status_checker = 0

if __name__ == "__main__":

    try:
        while True:
            api_status_checker += 1

            if api_status_checker == 50:
                api_status_checker = 0
                frontend_api.api_checker()

            sensor_data = serial_listener.get_data()

            if sensor_data:
                sensor_data = logic.data_converter(sensor_data)
                processed_data = data_manager.data_distributor(sensor_data)

                live_data = data_manager.live_data(processed_data)
                frontend_api.update_live_data(live_data)

                events = logic.event_warning(
                    processed_data, sensor_configs=config.SENSOR_CONFIGS
                )
                data_manager.event_distributor(events)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programm durch Benutzer beendet.")

    finally:
        frontend_api.stop_api_thread()
