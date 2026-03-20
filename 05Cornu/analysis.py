import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



# --- CONFIGURATION  ---
wavelength = 589.3 * 1e-9


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
                            float_format="%.2f",
                            position="H",
                            column_format="l" + "c" * (len(df.columns)-1))
    with open(FILE, "a") as f:
        f.write(latex_str + "\n\n")


#DATA LOADING
weight0 = pd.read_csv("data/weight_0.csv")
weight1 = pd.read_csv("data/weight_100.csv")
weight2 = pd.read_csv("data/weight_200.csv")
weight3 = pd.read_csv("data/weight_250.csv")

weightArray = [0.0, 100.0, 196.5, 249.7]


## OBSERVATION TABLES
def make_table(weight):
    table = pd.DataFrame({
        "$n$": [i+1 for i in range(len(weight.iloc[:,0]))],
        "left $\\unit{mm}$": weight.iloc[:,0],
        "right $\\unit{mm}$": weight.iloc[:,1],
        "top $\\unit{mm}$": weight.iloc[:,2],
        "bottom $\\unit{mm}$": weight.iloc[:,3],
        })
    return table

def save_table(weight, i):
    table = make_table(weight)
    save_latex_table(table, f"Readings for weight={weightArray[i]} g", f"tab:weight{i}", OBS_TABLES_FILE)

for i in range(len(weightArray)):
    save_table(globals()[f"weight{i}"], i)



## R0 ANALYSIS
dn1 = weight0.iloc[:,1] - weight0.iloc[:,0]
dn2 = weight0.iloc[:,3] - weight0.iloc[:,2]

#dn = np.concatenate((dn1,dn2), axis=0)
nArray = [1,2,3,4,5]

x_array = np.array(nArray)
y1_array = (dn1)**2 * 1e-6
y2_array = (dn2)**2 * 1e-6

def linear_fit(x, a, b):
    return a*x + b

params, covar = curve_fit(linear_fit, x_array, y1_array)
a, b = params

slope01 = a
save_latex_cmd("slopeZeroOne", slope01)

y_fit = linear_fit(x_array, a, b)
plt.scatter(x_array, y1_array, marker='o', color='black', label='left to right')
plt.plot(x_array, y_fit, linestyle='-', color='grey', label=f'slope = {slope01:.2e}')

params, covar = curve_fit(linear_fit, x_array, y2_array)
a, b = params

slope02 = a
save_latex_cmd("slopeZeroTwo", slope02)

y_fit = linear_fit(x_array, a, b)
plt.scatter(x_array, y2_array, marker='v', color='black', label='top to bottom')
plt.plot(x_array, y_fit, linestyle='--', color='grey', label=f'slope = {slope02:.2e}')

plt.title(r"Determiniation of $R_0$")
plt.xlabel(r"$n$")
plt.ylabel(r"$d_n^2$")

plt.grid()
plt.legend()
plt.savefig("plots/r0.png")
plt.show()

## CALCULATING R_0
R01 = slope01 / (4 * wavelength)
R02 = slope02 / (4 * wavelength)

save_latex_cmd('RZeroOne', R01)
save_latex_cmd('RZeroTwo', R01)

R0_avg = (R01 + R02)/2
save_latex_cmd('RZeroAvg', R0_avg)

print(R01, R02, R0_avg)
