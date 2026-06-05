import serial
import time
import csv
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import scipy.stats as stats

arduino_port = 'COM9'
baud_rate = 115200
timeout = 10

csv_file = 'arduino_data12.csv'
header = ["time(ms)", "sensor#1", "sensor#2", "sensor#3", "sensor#4", "LED1", "LED2", "LED3", "LED4"]

# collect Arduino data and write into csv
with open(csv_file, mode='w', newline='') as file:    
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
        print(f"connect successful {arduino_port}")
    except serial.SerialException:
        print(f" fail connect {arduino_port}")
        sys.exit()
    writer = csv.writer(file)
    writer.writerow(header)   

    print("begin")
    try:
        for _ in range(1200):
            data = ser.readline().decode().strip()
            data_list = data.split(', ')
            if (data_list == header):
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

# read csv
try:
    data = pd.read_csv(csv_file)
    print("successful!")
except FileNotFoundError:
    print(f"can't find the file {csv_file}, please check")
    sys.exit()

for sensor in ["sensor#1", "sensor#2", "sensor#3", "sensor#4"]:
    data[sensor] = pd.to_numeric(data[sensor], errors='coerce')

print("\n data:")
print(data.head())

# calculate simple reaction time
excel_file = "reaction_times.xlsx"
threshold = 100
led_sensor_map = {
    "LED1": "sensor#1",
    "LED2": "sensor#2",
    "LED3": "sensor#3",
    "LED4": "sensor#4"
}
column_names = ["LED1", "LED2", "LED3", "LED4"]

if os.path.exists(excel_file):
    old_df = pd.read_excel(excel_file)
    if list(old_df.columns) != column_names:
        print("column cannot pair")
else:
    old_df = pd.DataFrame(columns=column_names)

if not os.path.exists(csv_file):
    print(f"can't find the file': {csv_file}")
    sys.exit()

data = pd.read_csv(csv_file)
print(f"read CSV {csv_file}, line ={len(data)}.")

for s_col in led_sensor_map.values():
    data[s_col] = pd.to_numeric(data[s_col], errors='coerce')
for l_col in led_sensor_map.keys():
    data[l_col] = pd.to_numeric(data[l_col], errors='coerce')

time_vals = data["time(ms)"].values
num_rows = len(data)

reaction_times = {led: [] for led in led_sensor_map}

led_data = {led: data[led].values for led in led_sensor_map}
sen_data = {sen: data[sen].values for sen in led_sensor_map.values()}

i = 1
for led, sensor in led_sensor_map.items():
    i = 1
    while i < num_rows:
        prev_val = led_data[led][i - 1] if i > 0 else 0
        curr_val = led_data[led][i]
        if prev_val == 1 and curr_val == 0:
            t_on = time_vals[i]
            press_idx = None
            for j in range(i+1, num_rows):
                if sen_data[sensor][j] > threshold:
                    press_idx = j
                    break
            if press_idx is not None:
                rt = time_vals[press_idx] - t_on
                reaction_times[led].append(rt)
                i = press_idx
            else:
                i += 1
        else:
            i += 1
            print(i);

# find the maximum times of simple reaction
max_len = max(len(reaction_times[led]) for led in led_sensor_map)
# align the length of each column
for led in reaction_times:
    while len(reaction_times[led]) < max_len:
        reaction_times[led].append(np.nan)

new_block_df = pd.DataFrame({
    "LED1": reaction_times["LED1"],
    "LED2": reaction_times["LED2"],
    "LED3": reaction_times["LED3"],
    "LED4": reaction_times["LED4"]
})

combined_df = pd.concat([old_df, new_block_df], ignore_index=True)
combined_df.to_excel(excel_file, index=False)

print(f"Successfully added all reaction times of this experiment to {excel_file}."
      f"\nNow total line number = {len(combined_df)}.")
print("\nAll reaction times (head of new_block_df):")
print(new_block_df.head())

result_file = 'result.csv'
if os.path.exists(result_file) and not os.path.isdir(result_file):
    new_block_df.to_csv(result_file, mode='a', header=False, index=True)
else:
    new_block_df.to_csv(result_file, mode='w', index=True)

print("\n========== 8) Remove outliers in result.csv & compute stats ==========")

df_res = pd.read_csv(result_file, index_col=0)
print("Raw data from result.csv (head):")
print(df_res.head())

# remove outliers and check whether the data conforms to a normal distribution

filtered_map = {}  # save datas which are remove outliers

for col in df_res.columns:
    series_data = df_res[col].dropna()
    # use IQR to find outliers
    Q1 = series_data.quantile(0.25)
    Q3 = series_data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    filtered = series_data[(series_data >= lower_bound) & (series_data <= upper_bound)]
    filtered_map[col] = filtered

    max_val = filtered.max()
    min_val = filtered.min()
    mean_val = filtered.mean()
    std_val = filtered.std()

    print(f"\nColumn: {col} (outlier removed)")
    print(f"  Count= {len(filtered)}")
    print(f"  Max  = {max_val:.2f}")
    print(f"  Min  = {min_val:.2f}")
    print(f"  Mean = {mean_val:.2f}")
    print(f"  Std  = {std_val:.2f}")

    if len(filtered) >= 3:
        shapiro_stat, shapiro_p = stats.shapiro(filtered)
        print(f"  Shapiro-Wilk statistic = {shapiro_stat:.4f}, p-value = {shapiro_p:.4f}")
        if shapiro_p > 0.05:
            print("Cannot reject normality hypothesis, it may be a normal distribution (per column)")
        else:
            print("Rejecting the assumption of normality, it may not be a normal distribution (per column)")
    else:
        print("  (Not enough data points to run Shapiro-Wilk test)")

# combine datas, remove outliers and check whether the data conforms to a normal distribution

all_filtered = pd.concat([filtered_map["LED1"],
                          filtered_map["LED2"],
                          filtered_map["LED3"],
                          filtered_map["LED4"]], 
                         ignore_index=True)

all_filtered = all_filtered.dropna()

Q1_all = all_filtered.quantile(0.25)
Q3_all = all_filtered.quantile(0.75)
IQR_all = Q3_all - Q1_all
lower_all = Q1_all - 1.5 * IQR_all
upper_all = Q3_all + 1.5 * IQR_all
all_filtered_final = all_filtered[(all_filtered >= lower_all) & (all_filtered <= upper_all)]

print("\n--- Combine 4 columns (already outlier removed per column),")
print("    then outlier remove again in the merged set, and test normality. ---")
print(f"Count after merging = {len(all_filtered_final)}")

if len(all_filtered_final) >= 3:
    shapiro_stat_all, shapiro_p_all = stats.shapiro(all_filtered_final)
    print(f"  Merged Shapiro-Wilk statistic = {shapiro_stat_all:.4f}, p-value = {shapiro_p_all:.4f}")
    if shapiro_p_all > 0.05:
        print("Cannot reject normality hypothesis, it may be a normal distribution (merged data)")
    else:
        print("Rejecting the assumption of normality, it may not be a normal distribution (merged data)")
else:
    print("  (Not enough data points in merged data to run Shapiro-Wilk test)")

print("\nDone. See above for per-column & merged normality test results.")


# bar chart
for col in filtered_map:
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, len(filtered_map[col]) + 1), filtered_map[col], alpha=0.7)
    plt.xlabel("times of press")
    plt.ylabel("reaction time (ms)")
    plt.title(f"{col} reaction time(remove outliers)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{col}_reaction_time_filtered_bar_chart.png")  # save as PNG document
    plt.show()

# normal distribution chart
for col in filtered_map:
  
    plt.figure(figsize=(10, 6))

    # calculate mean and sd
    mean_val = filtered_map[col].mean()
    std_val = filtered_map[col].std()

    # produce histogram
    plt.hist(filtered_map[col], bins=30, density=True, alpha=0.7, color='blue', label=f'{col} histogram')

    # normal distribution curve
    xmin, xmax = plt.xlim() 
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mean_val, std_val)
    plt.plot(x, p, 'k', linewidth=2, label=f'Normal fit (mean={mean_val:.2f}, std={std_val:.2f})')

    plt.xlabel("Reaction Time (ms)")
    plt.ylabel("Probability Density")
    plt.title(f"{col} Reaction Time with Normal Distribution Fit (Outliers Removed)")


    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{col}_reaction_time_normal_distribution_fit.png")

    plt.show()


print("save successful")
