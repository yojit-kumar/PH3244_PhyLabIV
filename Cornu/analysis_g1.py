import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --- CONFIGURATION & CONSTANTS ---
wavelength = 589.3 * 1e-9  # Sodium lamp wavelength in meters
g = 9.81  # Acceleration due to gravity in m/s^2

# ---------------------------------------------------------

# ---------------------------------------------------------
L = 0.245   
w = 0.050   #
h = 0.00277  
# ---------------------------------------------------------

# File to save LaTeX commands/tables
RESULTS_FILE = "data/calculated_results.tex"
OBS_TABLES_FILE = "data/observation_tables.tex"
ANAL_TABLES_FILE = "data/analysis_tables.tex"

# Open files to clear them/start fresh
with open(RESULTS_FILE, "w") as f:
    f.write("")
with open(OBS_TABLES_FILE, "w") as f:
    f.write("% Auto-generated tables from analysis.py\n")
with open(ANAL_TABLES_FILE, "w") as f:
    f.write("% Auto-generated tables from analysis.py\n")

# Helper function to append to LaTeX files
def save_latex_cmd(name, value):
    with open(RESULTS_FILE, "a") as f:
        f.write(f"\\newcommand{{\\{name}}}{{\\SI{{{value:.4e}}}{{}}}}\n")

def save_latex_table(df, caption, label, FILE):
    # Generates a standard LaTeX table string
    latex_str = df.to_latex(index=False, 
                            caption=caption, 
                            label=label,
                            float_format="%.4e",
                            position="H",
                            column_format="l" + "c" * (len(df.columns)-1))
    with open(FILE, "a") as f:
        f.write(latex_str + "\n\n")


# --- DATA LOADING ---
weight0 = pd.read_csv("data/weight_0.csv")
weight2 = pd.read_csv("data/weight_200.csv") # 196.5g
weight3 = pd.read_csv("data/weight_250.csv") # 249.7g

# Removed 100g and 300g arrays
weightArray = [0.0, 196.5, 249.7]
masses_g = [196.5, 249.7] 
weights_data = [weight2, weight3]


# --- OBSERVATION TABLES ---
def make_table(weight):
    table = pd.DataFrame({
        "$n$": [i+1 for i in range(len(weight.iloc[:,0]))],
        "left $\\unit{mm}$": weight.iloc[:,0],
        "right $\\unit{mm}$": weight.iloc[:,1],
        "top $\\unit{mm}$": weight.iloc[:,2],
        "bottom $\\unit{mm}$": weight.iloc[:,3],
        })
    return table

save_latex_table(make_table(weight0), f"Readings for weight={weightArray[0]} g", "tab:weight0", OBS_TABLES_FILE)
for i, (wt, mass) in enumerate(zip(weights_data, masses_g)):
    save_latex_table(make_table(wt), f"Readings for weight={mass} g", f"tab:weight_{mass}", OBS_TABLES_FILE)


# --- R0 ANALYSIS ---
dn1 = weight0.iloc[:,1] - weight0.iloc[:,0]
dn2 = weight0.iloc[:,3] - weight0.iloc[:,2]

nArray = [1, 2, 3, 4, 5] # Assuming your baseline has 5 readings
x_array = np.array(nArray)
y1_array = (dn1)**2 * 1e-6
y2_array = (dn2)**2 * 1e-6

def linear_fit(x, a, b):
    return a*x + b

# Plotting R0
fig_R0 = plt.figure()

# Left to Right fit
params, covar = curve_fit(linear_fit, x_array, y1_array)
a1, b1 = params
slope01 = a1
save_latex_cmd("slopeZeroOne", slope01)
y_fit1 = linear_fit(x_array, a1, b1)
plt.scatter(x_array, y1_array, marker='o', color='black', label='left to right')
plt.plot(x_array, y_fit1, linestyle='-', color='grey', label=f'slope = {slope01:.2e}')

# Top to Bottom fit
params, covar = curve_fit(linear_fit, x_array, y2_array)
a2, b2 = params
slope02 = a2
save_latex_cmd("slopeZeroTwo", slope02)
y_fit2 = linear_fit(x_array, a2, b2)
plt.scatter(x_array, y2_array, marker='v', color='black', label='top to bottom')
plt.plot(x_array, y_fit2, linestyle='--', color='grey', label=f'slope = {slope02:.2e}')

plt.title(r"Determination of $R_0$")
plt.xlabel(r"$n$")
plt.ylabel(r"$d_n^2$")
plt.grid()
plt.legend()
plt.savefig("plots/r0.png")

# Calculating R0
R01 = slope01 / (4 * wavelength)
R02 = slope02 / (4 * wavelength)
save_latex_cmd('RZeroOne', R01)
save_latex_cmd('RZeroTwo', R02) 

R0_avg = (R01 + R02) / 2
save_latex_cmd('RZeroAvg', R0_avg)
print(f"R0 Calculations -> R01: {R01:.4e}, R02: {R02:.4e}, R0_avg: {R0_avg:.4e}")


# --- R1 & R2 ANALYSIS (SUBPLOTS) ---
def linear_fit_origin(x, m):
    return m * x # Line passing through origin for R1/R2 graphs

# Using the average of the two axes for a more accurate circular baseline for R1/R2
dn_sq = ((dn1**2 + dn2**2) / 2.0) * 1e-6 

# Changed to 1x2 subplots since we only have 2 weights now
fig_R1, axs_R1 = plt.subplots(1, 2, figsize=(12, 5))
fig_R2, axs_R2 = plt.subplots(1, 2, figsize=(12, 5))
# axs is already a 1D array if it's 1x2, so no need to flatten like before

R1_list = []
R2_list = []

for i, (wt, mass) in enumerate(zip(weights_data, masses_g)):
    
    # Dynamically handle the number of rings in case it differs
    N = len(wt)
    x_valid = 1.0 / np.arange(1, N + 1)
    
    # Calculate diameters for the bent beam
    dn_prime = (wt.iloc[:N, 1] - wt.iloc[:N, 0]).values      # Longitudinal (Shrinks)
    dn_prime_sq = (dn_prime**2) * 1e-6                       # convert mm^2 to m^2
    
    dn_dprime = (wt.iloc[:N, 3] - wt.iloc[:N, 2]).values     # Lateral (Expands)
    dn_dprime_sq = (dn_dprime**2) * 1e-6                     # convert mm^2 to m^2

    # Slice the baseline array to match the length of the current weight's data
    dn_sq_valid = dn_sq.iloc[:N].values

    # --- R1 Plotting ---
    y_R1 = (1.0 / dn_prime_sq) - (1.0 / dn_sq_valid)
    
    popt1, _ = curve_fit(linear_fit_origin, x_valid, y_R1)
    m1 = popt1[0]
    R1 = 1.0 / (4 * wavelength * m1)
    R1_list.append(R1)

    axs_R1[i].scatter(x_valid, y_R1, color='blue', label='Data')
    axs_R1[i].plot(x_valid, linear_fit_origin(x_valid, m1), 'k--', label=f'slope={m1:.2e}')
    axs_R1[i].set_title(r"$R_1$ Fit (Mass = {} g)".format(mass))
    axs_R1[i].set_xlabel(r"$1/n$")
    axs_R1[i].set_ylabel(r"$1/d_n'^2 - 1/d_n^2 \ (\mathrm{m}^{-2})$")
    axs_R1[i].legend()
    axs_R1[i].grid(True)

    # --- R2 Plotting ---
    y_R2 = np.abs((1.0 / dn_dprime_sq) - (1.0 / dn_sq_valid))
    
    popt2, _ = curve_fit(linear_fit_origin, x_valid, y_R2)
    m2 = popt2[0]
    R2 = 1.0 / (4 * wavelength * m2)
    R2_list.append(R2)

    axs_R2[i].scatter(x_valid, y_R2, color='red', label='Data')
    axs_R2[i].plot(x_valid, linear_fit_origin(x_valid, m2), 'k--', label=f'slope={m2:.2e}')
    axs_R2[i].set_title(r"$R_2$ Fit (Mass = {} g)".format(mass))
    axs_R2[i].set_xlabel(r"$1/n$")
    axs_R2[i].set_ylabel(r"$|1/d_n''^2 - 1/d_n^2| \ (\mathrm{m}^{-2})$")
    axs_R2[i].legend()
    axs_R2[i].grid(True)

fig_R1.tight_layout()
fig_R1.savefig("plots/r1_subplots.png")

fig_R2.tight_layout()
fig_R2.savefig("plots/r2_subplots.png")


# --- TABLES: R1, R2, POISSON, YOUNGS MODULUS ---

# 1. R1 and R2 Table
df_radii = pd.DataFrame({
    'Mass (g)': masses_g,
    '$R_1$ (m)': R1_list,
    '$R_2$ (m)': R2_list
})
save_latex_table(df_radii, "Calculated Values of Longitudinal ($R_1$) and Lateral ($R_2$) Bending Radii", "tab:radii", ANAL_TABLES_FILE)

# 2. Poisson's Ratio Table
poisson_ratio = np.array(R1_list) / np.array(R2_list)
df_poisson = pd.DataFrame({
    'Mass (g)': masses_g,
    '$\\zeta$ (Poisson Ratio)': poisson_ratio
})
df_poisson.loc[len(df_poisson.index)] = ['Mean', poisson_ratio.mean()]
save_latex_table(df_poisson, "Calculated Poisson Ratio", "tab:poisson", ANAL_TABLES_FILE)

# 3. Young's Modulus Table
Y_list = []
for mass, R1_val in zip(masses_g, R1_list):
    m_kg = mass / 1000.0
    # No zero check here anymore, so it will compute using the numbers provided at the top of the file
    Y = (12 * m_kg * g * L * R1_val) / (w * (h**3))
    Y_list.append(Y)

df_youngs = pd.DataFrame({
    'Mass (g)': masses_g,
    '$Y$ (Youngs Modulus, Pa)': Y_list
})
df_youngs.loc[len(df_youngs.index)] = ['Mean', np.mean(Y_list)]
save_latex_table(df_youngs, "Calculated Young's Modulus", "tab:youngs", ANAL_TABLES_FILE)

print("Analysis Complete! Subplots saved to /plots. Tables written to /data/analysis_tables.tex.")

# Display all figures at once at the end
plt.show()
