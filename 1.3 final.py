import serial
import time
import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


arduino_port = 'COM9'  
baud_rate = 115200     
timeout = 10           

csv_file = 'arduino_data12.csv'
header = ["time(ms)", "sensor#1", "sensor#2", "sensor#3", "sensor#4", "LED1", "LED2", "LED3", "LED4"]

# collect data
with open(csv_file, mode='w', newline='') as file:
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
        print("connect successful")
    except serial.SerialException:
        print("fail to connect")
        sys.exit()

    writer = csv.writer(file)
    writer.writerow(header) 
    print("begin")

    try:
        for _ in range(1200):
            data = ser.readline().decode().strip()
            data_list = data.split(', ')
            if data_list == header:
                break

        
        for _ in range(12000):
            data = ser.readline().decode().strip()
            print("data:", data)
            data_list = data.split(', ')
            writer.writerow(data_list)

    except KeyboardInterrupt:
        print("stop")


ser.close()
print(f"save as {csv_file}")

try:
    data = pd.read_csv(csv_file)
    print("successful!")
except FileNotFoundError:
    print(f"can't find the file {csv_file}, please check")
    sys.exit()

# Ensure that data is converted to numerical types for statistical analysis
sensor_cols = ["sensor#1", "sensor#2", "sensor#3", "sensor#4"]
for sensor in sensor_cols:
    data[sensor] = pd.to_numeric(data[sensor], errors='coerce')

print("\n data:")
print(data.head())

excel_file = "sensor_press_analysis.xlsx"
threshold = 100

df = data.copy()

press_list_1 = []
press_list_2 = []
press_list_3 = []
press_list_4 = []

sensor_press_map = {
    "sensor#1": press_list_1,
    "sensor#2": press_list_2,
    "sensor#3": press_list_3,
    "sensor#4": press_list_4,
}

# Traverse each sensor separately and find the pressing interval from ≤ threshold to>threshold
for sensor_col in sensor_cols:
    sensor_data = df[sensor_col].values

    in_press = False
    start_idx = 0

    for i in range(len(sensor_data)):
        val = sensor_data[i]

        # If a transition from 'not pressing' (≤ 100) to 'pressing' (>100) is detected
        if (not in_press) and (val > threshold):
            in_press = True
            start_idx = i

        # If a transition from 'press' (>100) to' not press' (≤ 100) is detected, the press ends
        elif in_press and (val <= threshold):
            end_idx = i - 1
            avg_val = df.loc[start_idx:end_idx, sensor_col].mean()
            sensor_press_map[sensor_col].append(avg_val)
            in_press = False

    if in_press:
        end_idx = len(sensor_data) - 1
        avg_val = df.loc[start_idx:end_idx, sensor_col].mean()
        sensor_press_map[sensor_col].append(avg_val)

# Align rows: Fill inconsistent length lists with 0 to avoid NaN
len_s1 = len(press_list_1)
len_s2 = len(press_list_2)
len_s3 = len(press_list_3)
len_s4 = len(press_list_4)

max_len = max(len_s1, len_s2, len_s3, len_s4)

def pad_with_zeros(lst, target_len):
    while len(lst) < target_len:
        lst.append(0)

pad_with_zeros(press_list_1, max_len)
pad_with_zeros(press_list_2, max_len)
pad_with_zeros(press_list_3, max_len)
pad_with_zeros(press_list_4, max_len)

df_final = pd.DataFrame({
    "sensor#1": press_list_1,
    "sensor#2": press_list_2,
    "sensor#3": press_list_3,
    "sensor#4": press_list_4
})

print(df_final.head(10))

if os.path.exists(excel_file):
    old_df = pd.read_excel(excel_file)
    combined_df = pd.concat([old_df, df_final], ignore_index=True)
    combined_df.to_excel(excel_file, index=False)
    print(f"Added write to {excel_file}, number of new lines added this time:{len(df_final)}")
else:
    df_final.to_excel(excel_file, index=False)
    print(f"Created and written to {excel_file}, new lines added this time: {len(df_final)}")

# Read the complete Excel again to obtain 'all historical data'
df_all = pd.read_excel(excel_file)

# Remove the middle 0 from all columns
new_data = {}
for col in df_all.columns:
    if col.startswith("sensor#"):
        non_zero_list = df_all[col][df_all[col] != 0].tolist()
        new_data[col] = non_zero_list
    else:
        pass

# Find the maximum length and align with zero
max_len_nozero = 0 if len(new_data)==0 else max(len(lst) for lst in new_data.values())

for col in new_data:
    while len(new_data[col]) < max_len_nozero:
        new_data[col].append(0)

df_nozero = pd.DataFrame(new_data)

print(df_nozero.head(10))

# Calculate the mean and standard deviation for each sensor press list
mean_std_data = {}
for col in df_nozero.columns:
    if col.startswith("sensor#"):
        mean_val = df_nozero[col].mean()
        std_val = df_nozero[col].std()
        mean_std_data[col] = {"mean": mean_val, "std": std_val}
        print(f"{col} - Mean: {mean_val:.2f}, Std: {std_val:.2f}")
        
# bar chart
sensor_cols_all = df_nozero.columns
for sensor_col in sensor_cols_all:
    plt.figure(figsize=(6, 4))
    plt.bar(range(len(df_nozero)), df_nozero[sensor_col], color='skyblue')
    plt.title(f"Press Average for {sensor_col} (no zero, all data)")
    plt.xlabel("Press Count (no-zero)")
    plt.ylabel("Force")
    plt.tight_layout()
    plt.show()

