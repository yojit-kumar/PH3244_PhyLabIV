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

voltage = df['Voltage (V)'].values
current = df['Current (I)'].values

# --- MULTI-COLUMN OBSERVATION TABLE ---
chunk_size = 21
chunks = [df.iloc[i:i+chunk_size].reset_index(drop=True) for i in range(0, len(df), chunk_size)]
multi_col_df = pd.concat(chunks, axis=1)

col_names = []
suffix_words = ["One", "Two", "Three", "Four"]
for i in range(len(chunks)):
    col_names.extend([f"Voltage {suffix_words[i]} (V)", f"Current {suffix_words[i]} ($10^{{-7}}$ A)"])
multi_col_df.columns = col_names

save_latex_table(multi_col_df, "Observation table for Franck-Hertz experiment.", "tab:fh_obs", OBS_TABLES_FILE, float_fmt="%.2f")

# --- DATA PROCESSING (Peak Finding & Interpolation) ---
# 1. Find the rough peak indices based on scale-appropriate prominence
rough_peaks_idx, _ = find_peaks(current, prominence=0.01, distance=5)

interp_peak_voltages = []
interp_peak_currents = []

# 2. Local Parabola Fitting
for idx in rough_peaks_idx:
    # Take a 5-point window centered on the rough peak
    start = max(0, idx - 2)
    end = min(len(voltage), idx + 3)
    
    x_window = voltage[start:end]
    y_window = current[start:end]
    
    # Fit a 2nd degree polynomial (y = ax^2 + bx + c)
    coeffs = np.polyfit(x_window, y_window, 2)
    a, b, c = coeffs
    
    # The true maximum of a downward facing parabola is at x = -b / (2a)
    if a < 0:
        x_peak = -b / (2 * a)
        # Ensure the mathematically calculated peak didn't drift wildly outside our window
        if x_window[0] <= x_peak <= x_window[-1]:
            y_peak = a * (x_peak**2) + b * x_peak + c
            interp_peak_voltages.append(x_peak)
            interp_peak_currents.append(y_peak)
        else:
            # Fallback to the raw peak if the fit goes out of bounds
            interp_peak_voltages.append(voltage[idx])
            interp_peak_currents.append(current[idx])
    else:
        # Fallback if the points accidentally fit an upward curve (rare, but safe)
        interp_peak_voltages.append(voltage[idx])
        interp_peak_currents.append(current[idx])

interp_peak_voltages = np.array(interp_peak_voltages)
interp_peak_currents = np.array(interp_peak_currents)

# Calculate the new, highly accurate differences between successive interpolated peaks
diffs = np.diff(interp_peak_voltages)
mean_diff = np.mean(diffs)
std_diff = np.std(diffs)

# --- FITTING & PLOTTING ---
plt.figure(figsize=(10, 6.5)) # Slightly taller to fit annotations
plt.plot(voltage, current, marker='o', linestyle='-', color='black', markersize=4, label='Recorded Data')
plt.plot(interp_peak_voltages, interp_peak_currents, "x", color='red', markersize=10, markeredgewidth=2, label='Interpolated Peaks')

# --- ANNOTATIONS ---
for i, (x, y) in enumerate(zip(interp_peak_voltages, interp_peak_currents)):
    # Label the peak voltage just above the red 'X'
    plt.text(x, y + 0.005, f"{x:.2f} V", ha='center', va='bottom', fontsize=9, color='darkred', fontweight='bold')
    
    # Draw dimension arrows and delta V labels between peaks
    if i > 0:
        prev_x = interp_peak_voltages[i-1]
        prev_y = interp_peak_currents[i-1]
        mid_x = (prev_x + x) / 2
        
        # Place the arrow slightly below the *lower* of the two peaks to avoid crossing the main curve
        arrow_y = min(prev_y, y) - 0.015 
        
        plt.annotate(
            '', xy=(x, arrow_y), xytext=(prev_x, arrow_y),
            arrowprops=dict(arrowstyle='<->', color='blue', shrinkA=0, shrinkB=0, lw=1)
        )
        # Label the Delta V exactly in the middle of the arrow
        plt.text(mid_x, arrow_y - 0.002, f"$\\Delta V \\approx {diffs[i-1]:.2f}$ V", ha='center', va='top', fontsize=9, color='blue')

plt.title("Franck-Hertz Data for Argon (with Peak Interpolation)")
plt.xlabel("Accelerating Voltage $V_{G2K}$ (V)")
plt.ylabel("Plate Current $I_p$ ($10^{-7}$ A)")
plt.ylim(bottom=0, top=max(current) + 0.02) # Give breathing room at the top for labels
plt.legend(loc='lower right') # Moved out of the way of the early peaks
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/franck_hertz_annotated.png")

# --- SAVE LATEX VARIABLES ---
save_latex_cmd("meanExcitation", mean_diff)
save_latex_cmd("stdExcitation", std_diff)
save_latex_cmd("totalPeaks", len(interp_peak_voltages))

print("Analysis Complete! Annotated plot saved to /plots. Tables and variables written to /data.")
