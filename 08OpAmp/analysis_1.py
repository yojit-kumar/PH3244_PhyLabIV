import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

sys.path.append("../lib/")
from latex_utils import *

run_before_start()

# ==========================================
# --- COMPONENT VALUES ---
# ==========================================
# 1. Inverting Amp (Set 1 & 2)
R_in_inv_One = 100.0    # Ohms
R_f_inv_One = 1000.0    # Ohms
R_in_inv_Two = 1000.0   # Ohms
R_f_inv_Two = 18000.0   # Ohms

# 2. Non-Inverting Amp (Set 1 & 2)
R_g_non_One = 100.0     # Ohms
R_f_non_One = 1000.0    # Ohms
R_g_non_Two = 1000.0    # Ohms
R_f_non_Two = 18000.0   # Ohms

# 3. Integrator (Set 1 & 2)
Vin_AC_int = 1.0        # Volts (AC RMS)
R1_int_One = 1000.0     # Ohms
C_actual_int_One = 0.1e-6  # Farads (0.1 uF)
R1_int_Two = 100.0      # Ohms
C_actual_int_Two = 0.05e-6 # Farads (0.05 uF)

# 4. Differentiator (Set 1 & 2)
Vin_AC_diff_One = 0.050    # Volts (AC RMS)
C_diff_One = 0.1e-6        # Farads (0.1 uF)
R2_actual_diff_One = 100000.0  # Ohms (100 kOhms)

Vin_AC_diff_Two = 0.010    # Volts (AC RMS)
C_diff_Two = 0.1e-6        # Farads (0.1 uF)
R2_actual_diff_Two = 100000.0  # Ohms (100 kOhms)

# ==========================================
# --- HELPER FUNCTIONS ---
# ==========================================
def linear_fit_origin(x, m):
    return m * x

def process_amplifier(file_path, set_name, is_inverting, R_in, R_f):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    vin = df['Vin'].values
    vout = df['Vout'].values
    
    # Fit line through origin
    popt, _ = curve_fit(linear_fit_origin, vin, vout)
    m_exp = popt[0]
    
    # Theoretical Gain & Caption Parameters
    if is_inverting:
        m_theo = -(R_f / R_in)
        prefix = "inv"
        param_str = f"$R_{{in}} = {R_in} \\ \\Omega$, $R_f = {R_f} \\ \\Omega$"
    else:
        m_theo = 1 + (R_f / R_in)
        prefix = "non"
        param_str = f"$R_g = {R_in} \\ \\Omega$, $R_f = {R_f} \\ \\Omega$"
        
    error = abs((m_exp - m_theo) / m_theo) * 100
    
    # Save Latex Variables
    save_latex_cmd(f"{prefix}ExpGain{set_name}", m_exp)
    save_latex_cmd(f"{prefix}TheoGain{set_name}", m_theo)
    save_latex_cmd(f"{prefix}Error{set_name}", error)
    
    # Create descriptive caption
    caption = f"Observation table for {prefix} amplifier (Set {set_name}). Parameters: {param_str}."
    
    # Save Observation Table
    save_latex_table(df, caption, f"tab:{prefix}_obs_{set_name}", OBS_TABLES_FILE, float_fmt="%.2f")
    
    return df, m_exp

def process_frequency_circuit(file_path, set_name, is_integrator, Vin, Known_Comp, Actual_Comp):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    freq = df['Frequency'].values
    vout = df['Vout'].values
    
    if is_integrator:
        y_val = Vin / vout  # |Vi / Vo|
        ylabel = "$|V_{in} / V_{out}|$"
    else:
        y_val = vout / Vin  # |Vo / Vi|
        ylabel = "$|V_{out} / V_{in}|$"
        
    df[ylabel] = y_val
    
    # Fit line through origin
    popt, _ = curve_fit(linear_fit_origin, freq, y_val)
    m_exp = popt[0]
    
    # Theoretical Extraction & Caption Parameters
    if is_integrator:
        calc_val = m_exp / (2 * np.pi * Known_Comp)
        prefix = "int"
        param_str = f"$V_{{in}} = {Vin}$ V, $R_1 = {Known_Comp} \\ \\Omega$, $C = {Actual_Comp}$ F"
    else:
        calc_val = m_exp / (2 * np.pi * Known_Comp)
        prefix = "diff"
        param_str = f"$V_{{in}} = {Vin}$ V, $C = {Known_Comp}$ F, $R_2 = {Actual_Comp} \\ \\Omega$"
        
    error = abs((calc_val - Actual_Comp) / Actual_Comp) * 100
    
    # Save Latex Variables
    save_latex_cmd(f"{prefix}Slope{set_name}", m_exp)
    save_latex_cmd(f"{prefix}CalcVal{set_name}", calc_val)
    save_latex_cmd(f"{prefix}ActualVal{set_name}", Actual_Comp)
    save_latex_cmd(f"{prefix}Error{set_name}", error)
    
    # Create descriptive caption
    caption = f"Observation table for {prefix} circuit (Set {set_name}). Parameters: {param_str}."
    
    # Save Observation Table
    save_latex_table(df, caption, f"tab:{prefix}_obs_{set_name}", OBS_TABLES_FILE, float_fmt="%.4f")
    
    return df, y_val, m_exp, ylabel

# ==========================================
# --- DATA PROCESSING & PLOTTING ---
# ==========================================

# 1. Inverting Amplifier
df_inv1, m_inv1 = process_amplifier("data/inv_1.csv", "One", True, R_in_inv_One, R_f_inv_One)
df_inv2, m_inv2 = process_amplifier("data/inv_2.csv", "Two", True, R_in_inv_Two, R_f_inv_Two)

plt.figure(figsize=(8, 5))
plt.scatter(df_inv1['Vin'], df_inv1['Vout'], label=f'Set 1 ($R_{{in}}$={R_in_inv_One}$\\Omega$, $R_f$={R_f_inv_One}$\\Omega$)', color='blue')
plt.plot(df_inv1['Vin'], linear_fit_origin(df_inv1['Vin'], m_inv1), 'b--', label=f'Set 1 Fit (Gain={m_inv1:.2f})')
plt.scatter(df_inv2['Vin'], df_inv2['Vout'], label=f'Set 2 ($R_{{in}}$={R_in_inv_Two}$\\Omega$, $R_f$={R_f_inv_Two}$\\Omega$)', color='red')
plt.plot(df_inv2['Vin'], linear_fit_origin(df_inv2['Vin'], m_inv2), 'r--', label=f'Set 2 Fit (Gain={m_inv2:.2f})')
plt.title("Inverting Amplifier Characteristics")
plt.xlabel("Input Voltage $V_{in}$ (V)")
plt.ylabel("Output Voltage $V_{out}$ (V)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/inverting_amp.png")

# 2. Non-Inverting Amplifier
df_non1, m_non1 = process_amplifier("data/noninv_1.csv", "One", False, R_g_non_One, R_f_non_One)
df_non2, m_non2 = process_amplifier("data/noninv_2.csv", "Two", False, R_g_non_Two, R_f_non_Two)

plt.figure(figsize=(8, 5))
plt.scatter(df_non1['Vin'], df_non1['Vout'], label=f'Set 1 ($R_g$={R_g_non_One}$\\Omega$, $R_f$={R_f_non_One}$\\Omega$)', color='blue')
plt.plot(df_non1['Vin'], linear_fit_origin(df_non1['Vin'], m_non1), 'b--', label=f'Set 1 Fit (Gain={m_non1:.2f})')
plt.scatter(df_non2['Vin'], df_non2['Vout'], label=f'Set 2 ($R_g$={R_g_non_Two}$\\Omega$, $R_f$={R_f_non_Two}$\\Omega$)', color='red')
plt.plot(df_non2['Vin'], linear_fit_origin(df_non2['Vin'], m_non2), 'r--', label=f'Set 2 Fit (Gain={m_non2:.2f})')
plt.title("Non-Inverting Amplifier Characteristics")
plt.xlabel("Input Voltage $V_{in}$ (V)")
plt.ylabel("Output Voltage $V_{out}$ (V)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/non_inverting_amp.png")

# 3. Integrator
df_int1, y_int1, m_int1, ylabel_int = process_frequency_circuit("data/int_1.csv", "One", True, Vin_AC_int, R1_int_One, C_actual_int_One)
df_int2, y_int2, m_int2, _ = process_frequency_circuit("data/int_2.csv", "Two", True, Vin_AC_int, R1_int_Two, C_actual_int_Two)

plt.figure(figsize=(8, 5))
plt.scatter(df_int1['Frequency'], y_int1, label='Set 1 Data', color='blue')
plt.plot(df_int1['Frequency'], linear_fit_origin(df_int1['Frequency'], m_int1), 'b--', label=f'Set 1 Fit (slope={m_int1:.2e})')
plt.scatter(df_int2['Frequency'], y_int2, label='Set 2 Data', color='red')
plt.plot(df_int2['Frequency'], linear_fit_origin(df_int2['Frequency'], m_int2), 'r--', label=f'Set 2 Fit (slope={m_int2:.2e})')
plt.title("Integrator Frequency Response")
plt.xlabel("Frequency (Hz)")
plt.ylabel(ylabel_int)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/integrator.png")

# 4. Differentiator
df_diff1, y_diff1, m_diff1, ylabel_diff = process_frequency_circuit("data/diff_1.csv", "One", False, Vin_AC_diff_One, C_diff_One, R2_actual_diff_One)
df_diff2, y_diff2, m_diff2, _ = process_frequency_circuit("data/diff_2.csv", "Two", False, Vin_AC_diff_Two, C_diff_Two, R2_actual_diff_Two)

plt.figure(figsize=(8, 5))
plt.scatter(df_diff1['Frequency'], y_diff1, label=f'Set 1 ($V_{{in}}$={Vin_AC_diff_One}V)', color='blue')
plt.plot(df_diff1['Frequency'], linear_fit_origin(df_diff1['Frequency'], m_diff1), 'b--', label=f'Set 1 Fit (slope={m_diff1:.2e})')
plt.scatter(df_diff2['Frequency'], y_diff2, label=f'Set 2 ($V_{{in}}$={Vin_AC_diff_Two}V)', color='red')
plt.plot(df_diff2['Frequency'], linear_fit_origin(df_diff2['Frequency'], m_diff2), 'r--', label=f'Set 2 Fit (slope={m_diff2:.2e})')
plt.title("Differentiator Frequency Response")
plt.xlabel("Frequency (Hz)")
plt.ylabel(ylabel_diff)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/differentiator.png")

print("Analysis Complete! 4 Plots saved to /plots. 8 Tables and all variables written to /data.")
