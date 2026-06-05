import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np


# 1) Read the Excel file
excel_file = "final choice.xlsx"  # Replace with your actual Excel filename/path
df = pd.read_excel(excel_file)

# 2) Filter rows where the "respond" column equals "Yes"
df_yes = df[df["respond"] == "Yes"]

# === Modified ===
# 3) Remove outliers using IQR (Interquartile Range) method
Q1 = df_yes["reaction time"].quantile(0.25)
Q3 = df_yes["reaction time"].quantile(0.75)
IQR = Q3 - Q1

# Define the bounds for non-outlier data
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter the data to remove outliers
df_yes_no_outliers = df_yes[(df_yes["reaction time"] >= lower_bound) & (df_yes["reaction time"] <= upper_bound)]

# === Modified ===
# 4) Compute statistics for the "reaction time" column after removing outliers
avg_val = df_yes_no_outliers["reaction time"].mean()
max_val = df_yes_no_outliers["reaction time"].max()
min_val = df_yes_no_outliers["reaction time"].min()
std_val = df_yes_no_outliers["reaction time"].std()

# 5) Print out the results
print("Statistics for 'reaction time' where 'respond' = Yes (after removing outliers):")
print(f"Mean = {avg_val:.2f}")
print(f"Max  = {max_val}")
print(f"Min  = {min_val}")
print(f"Std  = {std_val:.2f}")


# 6) Perform normality test (Shapiro-Wilk test) on the "reaction time" column
reaction_time_data = df_yes_no_outliers["reaction time"].dropna()  # Remove NaN values

# ========== A. Shapiro-Wilk Test ==========
shapiro_stat, shapiro_p = stats.shapiro(reaction_time_data)

print("Shapiro-Wilk Test:")
print(f"  Statistic = {shapiro_stat:.4f}, p-value = {shapiro_p:.4f}")

if shapiro_p > 0.05:
    print("  Conclusion: Cannot reject the null hypothesis, data may be normally distributed.")
else:
    print("  Conclusion: Reject the null hypothesis, data may not be normally distributed.")


# Q-Q Plot
fig = sm.qqplot(reaction_time_data, line='s')  
plt.title("Q-Q Plot for Reaction Time (No Outliers)")
plt.show()

# read two documents

file1 = "result.csv" 
file2 = "final choice.xlsx" 

df1 = pd.read_csv(file1)
df2 = pd.read_excel(file2)

reaction_series = df2["reaction time"]  

# combine datas

df1_col = df1.iloc[:, 0]  

combined_data = pd.concat([df1_col, reaction_series], ignore_index=True)

# Remove NaN and convert to numeric type
combined_data = pd.to_numeric(combined_data, errors='coerce').dropna()
# remove 0
combined_data = combined_data[combined_data != 0]
# remove outliers
Q1 = combined_data.quantile(0.25)
Q3 = combined_data.quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

filtered_data = combined_data[(combined_data >= lower_bound) & (combined_data <= upper_bound)]

# calculate max, min, mean and sd
max_val = filtered_data.max()
min_val = filtered_data.min()
mean_val = filtered_data.mean()
std_val = filtered_data.std()

print("\nStats for combined data (after outlier removal)")
print(f"Count = {len(filtered_data)}")
print(f"Max   = {max_val:.2f}")
print(f"Min   = {min_val:.2f}")
print(f"Mean  = {mean_val:.2f}")
print(f"Std   = {std_val:.2f}")

# Conduct normality test on the data after merging and removing outliers
if len(filtered_data) >= 3:
    shapiro_stat, shapiro_p = stats.shapiro(filtered_data)
    print(f"Shapiro-Wilk statistic = {shapiro_stat:.4f}, p-value = {shapiro_p:.4f}")
    if shapiro_p > 0.05:
        print("Combination: Cannot reject normality hypothesis, data may follow a normal distribution")
    else:
        print("Combination: Reject normality assumption, data may not follow a normal distribution")
else:
    print("not enough datas")

print(f"\nMerged data size after outlier removal: {len(filtered_data)}")
print(filtered_data.head(10))

