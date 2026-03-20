import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



# --- CONFIGURATION & UNCERTAINTIES ---



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
input_char = pd.read_csv("data/input_char.csv")
output_char_20 = pd.read_csv("data/output_char_20.csv")
output_char_50 = pd.read_csv("data/output_char_50.csv")
output_char_80 = pd.read_csv("data/output_char_80.csv")

input_VCC = np.array(["1.00 V", "3.00 V", "8.00 V"])
output_IB = np.array(["20 muA", "50 muA", "80 muA"])

marker = ['o', 's', '^']
linestyle = ['-', ':', '-.']

## INPUT CHARACTERSTIC ##
table_df = pd.DataFrame({
    "\\#": [i+1 for i in range(10)],
    "V$_{\\textrm{BE}}$ ($\\si{\\milli\\volt}$) 0": input_char.iloc[:,0],
    "I$_{\\textrm{B}}$ ($\\si{\\milli\\ampere}$) 0": input_char.iloc[:,1],
    "V$_{\\textrm{BE}}$ ($\\si{\\milli\\volt}$) 1": input_char.iloc[:,2],
    "I$_{\\textrm{B}}$ ($\\si{\\milli\\ampere}$) 1": input_char.iloc[:,3],
    "V$_{\\textrm{BE}}$ ($\\si{\\milli\\volt}$) 2": input_char.iloc[:,4],
    "I$_{\\textrm{B}}$ ($\\si{\\milli\\ampere}$) 2": input_char.iloc[:,5],
})

save_latex_table(table_df, f"Base Characterstic", f"tab:base_char", OBS_TABLES_FILE)

def linear_fit(x, a, b):
    return a * x + b

def input_fit(x, a, b, c):
    return a * np.exp(b*x) + c

plt.figure(figsize=(10,6))
i = 1
while i < 6:
    x_array = np.array(table_df.iloc[:,i]) * 1e-3
    y_array = np.array(table_df.iloc[:,i+1])

    log_y = np.log(y_array + 1e-15)

    params, covar = curve_fit(linear_fit, x_array, log_y)
    a, b  = params

    params, covar = curve_fit(input_fit, x_array, y_array, p0=[np.exp(b), a, 0], maxfev=5000)
    a, b, c = params

    x_smooth = np.linspace(min(x_array), max(x_array), 500)
    y_smooth = input_fit(x_smooth, a, b, c)

    c = int((i - 1)/2) 
    label = str( input_VCC[c] )
    plt.scatter(x_array, y_array, color='black', label=label, marker=marker[c])
    plt.plot(x_smooth, y_smooth, color='black', alpha=0.5, label=label, linestyle=linestyle[c])

    i += 2

plt.xlabel(r"V$_{\text{BE}}$ (V)")
plt.ylabel(r"I$_{\text{B}}$ (mA)")

plt.xlim(0.2,0.7)

plt.legend()
plt.grid()
plt.title("Base Characterstics")
plt.savefig("plots/base_char.png")
plt.show()





## OUTPUT CHARACTERSTIC ##
df_1 = pd.DataFrame({"\\#": [i+1 for i in range(13)]}) 
df_2 = pd.DataFrame({
    "V$_{\\textrm{CE}}$ ($\\si{\\volt}$) 0": output_char_20.iloc[:,0],
    "I$_{\\textrm{C}}$ ($\\si{\\milli\\ampere}$) 0": output_char_20.iloc[:,1],
    })
df_3 = pd.DataFrame({
    "V$_{\\textrm{CE}}$ ($\\si{\\volt}$) 1": output_char_50.iloc[:,0],
    "I$_{\\textrm{C}}$ ($\\si{\\milli\\ampere}$) 1": output_char_50.iloc[:,1],
    })
df_4 = pd.DataFrame({
    "V$_{\\textrm{CE}}$ ($\\si{\\volt}$) 2": output_char_80.iloc[:,0],
    "I$_{\\textrm{C}}$ ($\\si{\\milli\\ampere}$) 2": output_char_80.iloc[:,1],
    })
table_df = pd.concat([df_1, df_2, df_3, df_4], axis=1)

save_latex_table(table_df, f"Collector Characterstic", f"tab:collector_char", OBS_TABLES_FILE)

plt.figure(figsize=(10,6))
i = 1
while i < 6:
    x_array = np.array(table_df.iloc[:,i])
    x_array = x_array[~np.isnan(x_array)]
    y_array = np.array(table_df.iloc[:,i+1])
    y_array = y_array[~np.isnan(y_array)]

    params, covar = curve_fit(linear_fit, x_array[-6:], y_array[-6:])
    a, b = params

    x_smooth = np.linspace(min(x_array[-6:]), max(x_array), 500)
    y_smooth = linear_fit(x_smooth, a, b)

    c = int((i - 1)/2) 
    label = str( output_IB[c] )
    plt.scatter(x_array, y_array, color='black', label=label, marker=marker[c])
    plt.plot(x_smooth, y_smooth, color='black', alpha=0.5, label=label, linestyle=linestyle[c])

    i += 2

plt.xlabel(r"V$_{\text{CE}}$ (V)")
plt.ylabel(r"I$_{\text{C}}$ (mA)")

plt.xlim(0,8)

plt.legend()
plt.grid()
plt.title("Collector Characterstics")
plt.savefig("plots/collector_char.png")
plt.show()


# Create a nice table
#table_df = pd.DataFrame({
#    "\\#": [i+1 for i in range(len(curr_inc))],
#    "Current I (A)": curr_inc,
#    "Magnetic Field B (10G)": field_inc,
#    "B$^2$ (G$^2$)": (np.array(field_inc)*10)**2,
#})

#save_latex_table(table_df, f"Calibration Data (Increasing Current)", f"tab:calib_inc", CALIB_TABLES_FILE)





