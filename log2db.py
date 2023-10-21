import time
import json
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

i = 0

with open("5v.log") as fp:
    for line in fp.readlines():
        i += 1
        if i % 5 != 0:
            continue
        data = json.loads(line)

        # Extract temperature and humidity from the JSON response
        temperature = data['temp']
        humidity = data['humidity']

        # Generate timestamp
        timestamp = data['timestamp']

        cooler_state = data['cooler_state']

        # MySQL database connection
        connection = mysql.connector.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
        cursor = connection.cursor()

        # Insert data into the database
        insert_query = "INSERT INTO cabin (timestamp, cooler_state, temperature, humidity) VALUES (%s, %s, %s, %s)"
        data_to_insert = (timestamp, cooler_state, temperature, humidity)
        cursor.execute(insert_query, data_to_insert)
        connection.commit()

        # Close the database connection
        cursor.close()
        connection.close()

        print(f"Data inserted: Timestamp = {timestamp}, Cooling Status = {cooler_state}, Temperature = {temperature}, Humidity = {humidity}")


"""
CREATE TABLE cabin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    cooler_state BOOLEAN,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2)
);
"""