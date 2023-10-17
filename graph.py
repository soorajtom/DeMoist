import json
from datetime import datetime
import matplotlib.pyplot as plt
import math

# Initialize lists to store data
timestamps = []
temperatures = []
humidities = []

# Read the log file line by line (replace 'log.txt' with your log file path)
with open('values.log', 'r') as log_file:
    for line in log_file:
        data = json.loads(line)
        timestamps.append(data['timestamp'])
        temperatures.append(data['temp'])
        humidities.append(data['humidity'])

# Convert timestamp strings to datetime objects
timestamp_objects = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f') for ts in timestamps]

# Calculate dew point for each data point
dew_points = []
for temp, humidity in zip(temperatures, humidities):
    temp_celsius = temp  # Temperature in Celsius
    rel_humidity = humidity  # Relative humidity in percentage

    # Dew point calculation
    A = 17.271
    B = 237.7
    alpha = ((A * temp_celsius) / (B + temp_celsius)) + math.log(rel_humidity / 100.0)
    dew_point = (B * alpha) / (A - alpha)
    dew_points.append(dew_point)

# Create a figure with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

# Plot temperature on the first subplot
ax1.plot(timestamp_objects, temperatures, label='Temperature', color='blue')
ax1.set_ylabel('Temperature (°C)')
ax1.set_title('Temperature, Humidity, and Dew Point Over Time')
ax1.grid(True)
ax1.legend()

# Plot humidity on the second subplot
ax2.plot(timestamp_objects, humidities, label='Humidity', color='green')
ax2.set_ylabel('Humidity (%)')
ax2.grid(True)
ax2.legend()

# Plot dew point on the third subplot
ax3.plot(timestamp_objects, dew_points, label='Dew Point', color='red')
ax3.set_xlabel('Timestamp')
ax3.set_ylabel('Dew Point (°C)')
ax3.grid(True)
ax3.legend()

# Rotate x-axis labels for better readability (optional)
plt.xticks(rotation=45)

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
