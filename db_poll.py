import time
import requests
import mysql.connector
from mysql.connector import Error
from decouple import config
from datetime import datetime

# Load database configuration from .env.json
DATABASE_HOST = config('DATABASE_HOST')
DATABASE_NAME = config('DATABASE_NAME')
DATABASE_USER = config('DATABASE_USER')
DATABASE_PASSWORD = config('DATABASE_PASSWORD')

# HTTP URL for temperature and humidity data
read_url = 'http://192.168.1.112/read'
params_url = 'http://192.168.1.112/params'

# Polling interval in seconds
polling_interval = 5

setup_interval = 60
last_setup = 0

# MySQL database connection
connection = mysql.connector.connect(
    host=DATABASE_HOST,
    database=DATABASE_NAME,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD
)

def infolog(strval):
    print(strval)

def run():
    global last_setup
    while True:
        try:
            if last_setup % setup_interval == 0:
                last_setup = 0
                do_setup()
        except Exception as e:
            print(f"Error: {e}")

        try:
            # Send an HTTP GET request to the URL
            response = requests.get(read_url)
            data = response.json()  # Assuming the response is in JSON format

            # Extract temperature and humidity from the JSON response
            temperature = data['temp']
            humidity = data['humidity']

            # Generate timestamp
            timestamp = datetime.now()

            cooler_state = data['cooler_state']

            cursor = connection.cursor()

            # Insert data into the database
            insert_query = "INSERT INTO cabin (timestamp, cooler_state, temperature, humidity) VALUES (%s, %s, %s, %s)"
            data_to_insert = (timestamp, cooler_state, temperature, humidity)
            cursor.execute(insert_query, data_to_insert)
            connection.commit()

            # Close the database connection
            cursor.close()

            infolog(f"Data inserted: Timestamp = {timestamp}, Cooling Status = {cooler_state}, Temperature = {temperature}, Humidity = {humidity}")

        except Exception as e:
            infolog(f"Error: {e}")

        time.sleep(polling_interval)
        last_setup += polling_interval


def do_setup():
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cabin_config")
    set_data = cursor.fetchone()
    cursor.close()
    current_data = requests.get(params_url).json()
    for param in ["low", "high"]:
        if current_data[param] != set_data[param]:
            infolog("Setting %s from %s to %s" % (param, current_data[param], set_data[param]))
            requests.get("%s?%s=%s" % (params_url, param, set_data[param]))
    # for param in ["cooler_state", "cooler_fsm"]:
    #     if current_data[param] != int(set_data[param]):
    #         val = str(set_data[param]).lower()
    #         infolog("Setting %s from %s to %s" % (param, current_data[param], val))
    #         requests.get("%s?%s=%s" % (params_url, param, val))

if __name__ == "__main__":
    run()

"""
CREATE TABLE cabin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    cooler_state BOOLEAN,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2)
);
"""
"""
CREATE TABLE cabin_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cooler_fsm BOOLEAN,
    cooler_state BOOLEAN,
    high INTEGER,
    low INTEGER
);
"""
