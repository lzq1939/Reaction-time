import serial
import time
import csv
import os

arduino_port = "COM9"
baud_rate = 115200
timeout = 2

ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)


filename = "reaction_times.csv"

# Determine whether the file already exists
file_exists = os.path.exists(filename)

with open(filename, "a", newline="") as file:
    writer = csv.writer(file)

    # If the file does not exist before, write three columns of headers
    if not file_exists:
        writer.writerow(["Response", "ReactionTime", "StartTime"])

    print("Begin")

    try:
        while True:
            line = ser.readline().decode("utf-8").strip()
            if line:
                print(line)
                parts = line.split(",")
                writer.writerow(parts)  
                file.flush()          

    except KeyboardInterrupt:
        print("stop")

    finally:
        ser.close()
        print(f"Data has been added and written to {filename}")
