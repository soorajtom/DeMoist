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
    data = get_data_from_db()
    slope = calculate_smoothed_slope(data["humidity"])

    if not data:
        return "No data available."

    # Create separate Plotly graphs for temperature and humidity
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)

    if 'temperature' in data and len(data['temperature']) > 0:
        fig.add_trace(go.Scatter(x=data['timestamp'], y=data['temperature'], mode='lines', name='Temperature'), row=3, col=1)
        fig.update_yaxes(title_text='Temperature (°C)', row=3, col=1)
    
    fig.add_trace(go.Scatter(x=data['timestamp'], y=slope, mode='lines', name='Humidity Change'), row=2, col=1)
    fig.update_yaxes(title_text='dH/dt', row=2, col=1)

    if 'humidity' in data and len(data['humidity']) > 0:
        fig.add_trace(go.Scatter(x=data['timestamp'], y=data['humidity'], mode='lines', name='Humidity'), row=1, col=1)
        fig.update_yaxes(title_text='Humidity (%)', row=1, col=1)

    # Customize the layout
    fig.update_layout(title='Temperature and Humidity',
                      xaxis_title='Timestamp',
                      height=750)

    # Plotly graphs to HTML
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
            query = "SELECT COUNT(*) FROM cabin"

            # Execute the query
            cursor.execute(query)

            # Fetch the result

            count = cursor.fetchone()["COUNT(*)"]
            # skip_plus_one = count/500
            skip_plus_one = 1

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT *\
            FROM (\
            SELECT *, ROW_NUMBER() OVER (ORDER BY timestamp DESC) AS row_num\
            FROM cabin\
            ) AS subquery\
            WHERE row_num %% %d = 0;" %(skip_plus_one))
            data_list = cursor.fetchall()
            cursor.close()
            connection.close()
            temps = []
            humidity = []
            cooler_states = []
            timestamps = []
            data_list.reverse()
            for data in data_list:
                temps.append(data['temperature'])
                humidity.append(data['humidity'])
                cooler_states.append(int(data['cooler_state'])*5)
                timestamps.append(data['timestamp'])
            return {"temperature": temps, "humidity": humidity, "cooler_states": cooler_states, "timestamp": timestamps}

    except Error as e:
        print(f"Error: {e}")

def calculate_smoothed_slope(data):
    # Calculate the smoothed slope using central difference and a rolling average
    window_size = 120  # Adjust the window size as needed
    smoothed_data = [sum(data[i:i+window_size]) / window_size for i in range(len(data) - window_size + 1)]
    slope = []
    slope_value = 0
    for i in range(len(smoothed_data)):
        if i == 0:
            slope.append(0)
        elif i == len(smoothed_data) - 1:
            slope.append(slope_value)
        else:
            slope_value = ((smoothed_data[i + 1] - smoothed_data[i - 1]) / 2) * 12
            slope.append(slope_value)
    return slope

if __name__ == '__main__':
    app.run(debug=True)

"""
SELECT *
FROM (
SELECT *, ROW_NUMBER() OVER (ORDER BY timestamp DESC) AS row_num
FROM cabin
) AS subquery
WHERE row_num % 1 = 0;
"""