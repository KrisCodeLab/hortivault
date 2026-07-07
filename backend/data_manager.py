import json
import psycopg2 as psql

class DataManager:


    def __init__(self, DATABASE, HOST, PORT, USER, PASSWORD):
        self.database = DATABASE
        self.host = HOST
        self.port = PORT
        self.user = USER
        self.password = PASSWORD
        self.sensor_cache = {}

        self.connection = None
        self._connect()

        


    def _connect(self):
        """Verbindung zur PostgreSQL DB aufbauen"""
        try:
            print(f"[SYSTEM]: Verbindung zu {self.database} aufbauen...")
            self.connection = psql.connect(dbname=self.database, 
                                        host=self.host, 
                                        port=self.port, 
                                        user=self.user, 
                                        password=self.password)
        except psql.OperationalError as e:
            self.connection = None
            print(f"[DB ERROR]: {e}")


    def _data_reader(self, sensor_data):
        """Verarbeitet das Datenpaket des USB-Listeners und bereitet es zur Speicherung in die DB vor."""
        processed_data = []

        for sensor, data in sensor_data.items():
            sensor_name = sensor
            measurements = {"real": data["real"], "raw": data["raw"]}
            is_test = data["is_test"]
                
            data_pack = {
                "sensor_name": sensor_name,
                "measurements": measurements,
                "is_test": is_test
            }

            processed_data.append(data_pack)
        return processed_data
    

    def _live_data(self, processed_data):
        """Ausgabe der Live Daten"""
        for data_pack in processed_data:
            sensor_name = data_pack["sensor_name"]
            measurements = data_pack["measurements"]["real"]
            
            print(f"{sensor_name}:")
            print(f"{measurements}\n")
            

    def _db_import(self, processed_data):
        """Import der Daten in die PostreSQL Datenbank"""
        if self.connection is None:
            self._connect()

        if self.connection is None:
            return
        
        try:
            cursor = self.connection.cursor()
        
            for data_pack in processed_data:
                sensor_id = self._sensor_id_checker(data_pack["sensor_name"])

                if sensor_id is None:
                    continue

                measurements = json.dumps(data_pack["measurements"])
                is_test = data_pack["is_test"]

                sql_command = "INSERT INTO sensor_data (sensor_id, measurements, is_test) VALUES (%s, %s, %s)"
                cursor.execute(sql_command, (sensor_id, measurements, is_test))

            self.connection.commit()   
            cursor.close()

        except psql.OperationalError as e:
            self.connection = None
            print(f"[DB ERROR]: {e}")

    
    def _sensor_id_checker(self, sensor_name):
        """Überprüft ob sich ein Sensor im cache oder in der DB befindet und gibt dessen ID zurück"""
        if sensor_name in self.sensor_cache:
            return self.sensor_cache[sensor_name]

        if self.connection is None:
            self._connect()

        if self.connection is None:
            return
        
        try:
            cursor = self.connection.cursor()
            sql_command = "SELECT id FROM sensors WHERE name = %s"
            
            cursor.execute(sql_command, (sensor_name,))
            result = cursor.fetchone()

            if result is None:
                    print(f"[DB ERROR]: Sensor '{sensor_name}' ist unbekannt in der HortiVault Datenbank!")
                    return

            sensor_id = result[0]
            cursor.close()

            self.sensor_cache[sensor_name] = sensor_id

            return sensor_id
        
        except psql.OperationalError as e:
            self.connection = None
            print(f"[DB ERROR]: {e}")


    def data_distributor(self, sensor_data):
        """
        Methode für main.py, in welcher folgende Methoden aufgerufen werden: 
        _data_reader
        _live_data
        _db_import
        """
        processed_data = self._data_reader(sensor_data)

        self._live_data(processed_data)
        self._db_import(processed_data)

        return processed_data


    def event_distributor(self, events):
        """
        Filter das Event "event_ok" aus, überwacht Zustandsänderungen von zu lösenden Events 
        und updatet die Tabelle events.
        """
        if self.connection is None:
            self._connect()

        if self.connection is None:
            return
        
        try:
            cursor = self.connection.cursor()

            for event_pack in events:
                sensor_id = self._sensor_id_checker(event_pack["sensor_name"])

                if sensor_id is None:
                    continue
                
                measurement = event_pack["measurement"]
                new_event = event_pack["event"]

                sql_command = "SELECT event, resolved FROM events WHERE sensor_id = %s and measurement_type = %s and resolved = false"
                cursor.execute(sql_command, (sensor_id, measurement))
                result = cursor.fetchone()
                if result is not None:
                    event = result[0]
                    resolved = result[1]
                else:
                    event = None
                    resolved = None

                # keine Warnmeldung und keine ungelösten Events in der DB
                if resolved is None and new_event == "event_ok":
                    print("keine Warnmeldung und keine ungelösten Events in der DB")
                    continue
                
                # bestehendes ungelöstes Event
                if resolved is False and new_event == event:
                    print("bestehendes ungelöstes Event")
                    continue

                # offenes Event gelöst und kein neues Event getriggert
                if resolved is False and new_event == "event_ok":
                    print("offenes Event gelöst und kein neues Event getriggert")
                    sql_command = "UPDATE events SET resolved = true WHERE sensor_id = %s and measurement_type = %s"
                    cursor.execute(sql_command, (sensor_id, measurement))
                    continue
                
                # neues zu lösendes Event mit keinen offenen Events in der DB
                if resolved is None and new_event != "event_ok":
                    print("neues zu lösendes Event mit keinen offenen Events in der DB")
                    value = event_pack["value"]

                    sql_command = "INSERT INTO events (sensor_id, measurement_type, event, triggered_value) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_command, (sensor_id, measurement, new_event, value))
                    continue

                # Zustandsänderung von einem alten zu einem neuen zu lösenden Event
                print("Zustandsänderung von einem alten zu einem neuen zu lösenden Event")
                if resolved is False and new_event != event:
                    sql_command = "UPDATE events SET resolved = true WHERE sensor_id = %s and measurement_type = %s"
                    cursor.execute(sql_command, (sensor_id, measurement))

                    value = event_pack["value"]

                    sql_command = "INSERT INTO events (sensor_id, measurement_type, event, triggered_value) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_command, (sensor_id, measurement, new_event, value))
                    continue

            self.connection.commit()   
            cursor.close()
        
        except psql.OperationalError as e:
            self.connection = None
            print(f"[DB ERROR]: {e}")      
