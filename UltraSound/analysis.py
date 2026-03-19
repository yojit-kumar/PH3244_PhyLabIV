import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --- CREATE DIRECTORIES ---
os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

# --- CONFIGURATION & CONSTANTS ---
wavelength = 655e-9  # Laser wavelength in meters
L = 1.319  # Distance between crystal and detector in meters
f = 3.2e6  # Frequency of crystal in Hz

RESULTS_FILE = "data/calculated_results.tex"
OBS_TABLES_FILE = "data/observation_tables.tex"
ANAL_TABLES_FILE = "data/analysis_tables.tex"

# Clear out old files to start fresh
with open(RESULTS_FILE, "w") as file: file.write("")
with open(OBS_TABLES_FILE, "w") as file: file.write("% Auto-generated observation tables\n")
with open(ANAL_TABLES_FILE, "w") as file: file.write("% Auto-generated analysis tables\n")

# --- HELPER FUNCTIONS ---
def save_latex_cmd(name, value):
    with open(RESULTS_FILE, "a") as file:
        # Saving variable values in scientific notation
        file.write(f"\\newcommand{{\\{name}}}{{\\SI{{{value:.4e}}}{{}}}}\n")

def save_latex_table(df, caption, label, filepath, float_fmt="%.4e"):
    # Generates a standard LaTeX table string
    latex_str = df.to_latex(index=False, 
                            caption=caption, 
                            label=label,
                            float_format=float_fmt,
                            position="H",
                            column_format="c" * len(df.columns))
    with open(filepath, "a") as file:
        file.write(latex_str + "\n\n")

# --- DATA LOADING & CLEANING ---
sine_df = pd.read_csv("data/sine.csv")
square_df = pd.read_csv("data/square.csv")

# Strip any accidental leading/trailing spaces from column headers
sine_df.columns = sine_df.columns.str.strip()
square_df.columns = square_df.columns.str.strip()

# Create clean observation tables
sine_obs = sine_df.copy()
sine_obs.rename(columns={'order': '$n$', 'distance': 'Distance (mm)'}, inplace=True)
save_latex_table(sine_obs, "Observation table for Sine wave signal.", "tab:sine_obs", OBS_TABLES_FILE, float_fmt="%.2f")

sq_obs = square_df.copy()
sq_obs.rename(columns={'order': '$n$', 'distance': 'Distance (mm)'}, inplace=True)
save_latex_table(sq_obs, "Observation table for Square wave signal.", "tab:sq_obs", OBS_TABLES_FILE, float_fmt="%.2f")

# --- DATA PROCESSING ---
def process_data(df):
    # Locate the distance at order 0
    x0 = df.loc[df['order'] == 0, 'distance'].values[0]
    df['D_mm'] = np.abs(df['distance'] - x0)
    df['D_m'] = df['D_mm'] * 1e-3
    
    # Drop order 0 for lambda/V calculation to prevent division by zero
    calc_df = df[df['order'] > 0].copy()
    calc_df['theta'] = np.arctan(calc_df['D_m'] / L)
    calc_df['Lambda'] = (calc_df['order'] * wavelength) / np.sin(calc_df['theta'])
    calc_df['V'] = f * calc_df['Lambda']
    
    return df, calc_df

sine_df, sine_calc = process_data(sine_df)
square_df, square_calc = process_data(square_df)

# --- FITTING & PLOTTING ---
def linear_fit_origin(x, m):
    return m * x # Forces line through the origin

popt_sine, _ = curve_fit(linear_fit_origin, sine_calc['order'], sine_calc['D_m'])
m_sine = popt_sine[0]
V_fit_sine = f * (wavelength * L) / m_sine

popt_sq, _ = curve_fit(linear_fit_origin, square_calc['order'], square_calc['D_m'])
m_sq = popt_sq[0]
V_fit_sq = f * (wavelength * L) / m_sq

plt.figure(figsize=(9, 6))
plt.scatter(sine_calc['order'], sine_calc['D_m'], color='blue', label='Sine Data')
plt.plot(sine_calc['order'], linear_fit_origin(sine_calc['order'], m_sine), 'b--', label=f'Sine Fit (slope={m_sine:.4e})')

plt.scatter(square_calc['order'], square_calc['D_m'], color='red', marker='s', label='Square Data')
plt.plot(square_calc['order'], linear_fit_origin(square_calc['order'], m_sq), 'r-', label=f'Square Fit (slope={m_sq:.4e})')

plt.title("Diffraction Spot Distance ($D_n$) vs Order ($n$)")
plt.xlabel("Order ($n$)")
plt.ylabel("Distance $D_n$ (m)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/diffraction_fit.png")

# --- ANALYSIS TABLES ---
def create_analysis_table(calc_df):
    table = pd.DataFrame({
        "$n$": calc_df['order'],
        "$D_n$ (m)": calc_df['D_m'],
        "$\\theta_n$ (rad)": calc_df['theta'],
        "$\\Lambda$ (m)": calc_df['Lambda'],
        "$V$ (m/s)": calc_df['V']
    })
    return table

save_latex_table(create_analysis_table(sine_calc), "Calculated values for Sine wave.", "tab:sine_calc", ANAL_TABLES_FILE)
save_latex_table(create_analysis_table(square_calc), "Calculated values for Square wave.", "tab:sq_calc", ANAL_TABLES_FILE)

# --- SAVE LATEX VARIABLES ---
# Using strictly alphabetical names (e.g., sqSlope instead of squareSlope) to avoid clashing with built-in LaTeX commands
save_latex_cmd("laserWavelength", wavelength)
save_latex_cmd("crystalFreq", f)
save_latex_cmd("detectorDist", L)

save_latex_cmd("sineSlope", m_sine)
save_latex_cmd("sqSlope", m_sq)

save_latex_cmd("sineMeanV", sine_calc['V'].mean())
save_latex_cmd("sqMeanV", square_calc['V'].mean())

save_latex_cmd("sineFitV", V_fit_sine)
save_latex_cmd("sqFitV", V_fit_sq)

print("Analysis Complete! Plot saved to /plots. Tables and variables written to /data.")
