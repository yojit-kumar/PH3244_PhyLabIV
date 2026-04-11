import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

sys.path.append("../lib/")
from latex_utils import *

run_before_start()

# --- DATA LOADING & CLEANING ---
df = pd.read_csv("data/franck_hertz.csv")
df.columns = df.columns.str.strip()

# Make sure columns match your exact CSV headers if they differ slightly
voltage = df['Voltage (V)'].values
current = df['Current (I)'].values

# --- MULTI-COLUMN OBSERVATION TABLE ---
# Reshape the 84 rows into 4 chunks of 21 rows to save vertical space
chunk_size = 21
chunks = [df.iloc[i:i+chunk_size].reset_index(drop=True) for i in range(0, len(df), chunk_size)]
multi_col_df = pd.concat(chunks, axis=1)

# Generate column names using words to avoid any number-related LaTeX command issues down the line
col_names = []
suffix_words = ["One", "Two", "Three", "Four"]
for i in range(len(chunks)):
    col_names.extend([f"Voltage {suffix_words[i]} (V)", f"Current {suffix_words[i]} ($10^{{-7}}$ A)"])
multi_col_df.columns = col_names

# Save the reshaped table
save_latex_table(multi_col_df, "Observation table for Franck-Hertz experiment.", "tab:fh_obs", OBS_TABLES_FILE, float_fmt="%.2f")

# --- DATA PROCESSING (Peak Finding) ---
# find_peaks relies on the shape of the curve. 
# Note: You may need to tweak 'prominence' or 'distance' depending on the exact noise in your data.
peaks_idx, _ = find_peaks(current, prominence=0.04, distance=5)
peak_voltages = voltage[peaks_idx]
peak_currents = current[peaks_idx]

# Calculate differences between successive peaks
diffs = np.diff(peak_voltages)
mean_diff = np.mean(diffs)
std_diff = np.std(diffs)

# --- FITTING & PLOTTING ---
plt.figure(figsize=(9, 6))
plt.plot(voltage, current, marker='o', linestyle='-', color='black', markersize=4, label='Recorded Data')
plt.plot(peak_voltages, peak_currents, "x", color='red', markersize=10, markeredgewidth=2, label='Identified Peaks')

plt.title("Franck-Hertz Data for Argon")
plt.xlabel("Accelerating Voltage $V_{G2K}$ (V)")
plt.ylabel("Plate Current $I_p$ ($10^{-7}$ A)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/franck_hertz.png")

# --- SAVE LATEX VARIABLES ---
# Using strict alphabetical names as requested (no numbers or hyphens)
save_latex_cmd("meanExcitation", mean_diff)
save_latex_cmd("stdExcitation", std_diff)
save_latex_cmd("totalPeaks", len(peak_voltages))

print("Analysis Complete! Plot saved to /plots. Tables and variables written to /data.")
