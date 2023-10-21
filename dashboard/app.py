from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from decouple import config
from datetime import datetime

# Load database configuration from .env.json
DATABASE_HOST = config('DATABASE_HOST')
DATABASE_NAME = config('DATABASE_NAME')
DATABASE_USER = config('DATABASE_USER')
DATABASE_PASSWORD = config('DATABASE_PASSWORD')

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch data from the database
    data_list = get_data_from_db()
    temps = []
    humidity = []
    cooler_states = []
    timestamps = []
    for data in data_list:
        temps.append(data['temperature'])
        humidity.append(data['humidity'])
        cooler_states.append(int(data['cooler_state'])*5)
        timestamps.append(data['timestamp'])

    # Create a Plotly graph
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Scatter(x=timestamps, y=temps, mode='lines+markers', name='Temperature'))
    fig.add_trace(go.Scatter(x=timestamps, y=humidity, mode='lines+markers', name='Humidity'))
    fig.add_trace(go.Scatter(x=timestamps, y=cooler_states, mode='lines', name='Cooler Status'))

    # Customize the layout
    fig.update_layout(title='Temperature, Humidity, and Cooler State',
                      xaxis_title='Timestamp',
                      yaxis_title='Value')

    # Plotly graph to HTML
    graph_json = fig.to_json()

    return render_template('index.html', graph_json=graph_json)

def get_data_from_db():
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host=DATABASE_HOST,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT timestamp, temperature, humidity, cooler_state FROM cabin ORDER BY timestamp DESC LIMIT 5000")
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            return data

    except Error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)
