import requests
import json
import time
from datetime import datetime
import matplotlib.pyplot as plt

# Define the endpoint URL
endpoint_url = 'http://192.168.0.203/read'  # Replace with your actual endpoint URL

# Define the polling interval in seconds (e.g., 60 seconds for once per minute)
polling_interval = 1

# Lists to store timestamps, data values 1, and data values 2 for plotting
timestamps = []
data_values_1 = []
data_values_2 = []

# # Create the figure and axes objects
# plt.figure(figsize=(10, 6))
# ax = plt.gca()

# # Turn on interactive mode
# plt.ion()

while True:
    try:
        # Make an HTTP GET request to the endpoint
        response = requests.get(endpoint_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            # # Get the values you want to plot (replace 'value_key1' and 'value_key2' with actual keys)
            # value_to_plot_1 = data.get('temp')  # Replace 'value_key1' with the actual key
            # value_to_plot_2 = data.get('humidity')  # Replace 'value_key2' with the actual key

            # Get the current timestamp
            timestamp = datetime.now()
            data["timestamp"] = str(timestamp)

            # Append the timestamp and data values to the lists
            # timestamps.append(timestamp)
            # data_values_1.append(value_to_plot_1)
            # data_values_2.append(value_to_plot_2)

            # Log the JSON response with the timestamp (optional)
            with open('values.log', 'a') as log_file:
                log_file.write(json.dumps(data) + "\n")

            # # Clear the previous plot and redraw it with updated data
            # ax.clear()
            # ax.plot(timestamps, data_values_1, marker='o', linestyle='-', label='Value 1')
            # ax.plot(timestamps, data_values_2, marker='x', linestyle='--', label='Value 2')
            # ax.set_xlabel('Timestamp')
            # ax.set_ylabel('Values')
            # ax.set_title('Values Over Time')
            # ax.legend()  # Add a legend to differentiate between the two lines
            # ax.grid(True)
            # plt.tight_layout()

            # # Draw the updated plot
            # plt.draw()

        else:
            print(f'Failed to retrieve data. Status code: {response.status_code}')

    except Exception as e:
        print(f'Error: {str(e)}')

    # Wait for the polling interval before the next request
    time.sleep(polling_interval)