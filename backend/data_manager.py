import json
import psycopg2 as psql

class DataManager:


    def __init__(self, DATABASE, HOST, PORT, USER, PASSWORD):
        self.database = DATABASE
        self.host = HOST
        self.port = PORT
        self.user = USER
        self.password = PASSWORD

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
                sql_command = "SELECT id FROM sensors WHERE name = %s"
                sensor_name = data_pack["sensor_name"]
                cursor.execute(sql_command, (sensor_name,))
                result = cursor.fetchone()

                # --------------------------------------
                ### Zeile 73 - 78 lediglich für Testbetrieb und unvollständiger sensors Tabelle notwendig ###
                if result is None:
                    print(f"[DB ERROR]: Sensor '{sensor_name}' ist unbekannt im hortivault-System. Werte wurden nicht in DB gespeichert!")
                    continue
                # --------------------------------------
                
                sensor_id = result[0]
                measurements = json.dumps(data_pack["measurements"])
                is_test = data_pack["is_test"]

                sql_command = "INSERT INTO sensor_data (sensor_id, measurements, is_test) VALUES (%s, %s, %s)"
                cursor.execute(sql_command, (sensor_id, measurements, is_test))

            self.connection.commit()   
            cursor.close()

        except psql.OperationalError as e:
            self.connection = None
            print(f"[DB ERROR]: {e}")


    def data_distributor(self, sensor_data):
        """
        Methode für main.py, in welcher folgende Methoden aufgerufen werde: 
        _data_reader
        _live_data
        _db_import
        """
        processed_data = self._data_reader(sensor_data)

        self._live_data(processed_data)
        self._db_import(processed_data)
