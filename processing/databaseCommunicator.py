from influxdb import InfluxDBClient

# Initialize the connection to the DB
INFLUXDB_ADDRESS = 'hostname'
INFLUXDB_USER = 'user'
INFLUXDB_PASSWORD = 'pw'
INFLUXDB_SENSOR_DATABASE = 'db'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


def init_influxdb_database():
    """
    The function _init_influxdb_database() initializes the InfluxDB database.
    If the database does not exist, it will be created through the function.
    """
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_SENSOR_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_SENSOR_DATABASE)
    influxdb_client.switch_database(INFLUXDB_SENSOR_DATABASE)


def send_data_to_influxdb(data):
    """
    Sends data to the database
    :param data: Has the form {"measurement": measurement, "tags" : {...}, "time": time, fields: {...} }
    """
    influxdb_client.write_points([data])


def get_info():
    """
    Checks the database
    """
    print(influxdb_client.get_list_database())
    print(influxdb_client.query('SELECT "timestamp" FROM "sensor_data" '))

