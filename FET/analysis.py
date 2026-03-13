import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


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
drain_0 = pd.read_csv("data/drain_0.csv")
drain_0245 = pd.read_csv("data/drain_0245.csv")
drain_1 = pd.read_csv("data/drain_1.csv")

output_2 = pd.read_csv("data/transfer_2.csv")
output_405 = pd.read_csv("data/transfer_405.csv")
output_602 = pd.read_csv("data/transfer_602.csv")

VGSarray = np.array([0.0, -0.245, -1.0])
VDSarray = np.array([2.0, 4.05, 6.02])

marker = ['o', 's', '^']
linestyle = ['-', ':', '-.']





def linear_fit(x, a, b):
    return a*x + b

def drain_plot(dataFrame, i):
    x_array = np.array(dataFrame.iloc[:,0])
    y_array = np.array(dataFrame.iloc[:,1])

    #x_fit = x_array[-7:]
    #y_fit = y_array[-7:]

    #params, covar = curve_fit(linear_fit, x_fit, y_fit)
    #a, b = params

    #x_fit = np.linspace(np.min(x_fit), np.max(x_fit), 500)
    #y_fit = linear_fit(x_fit, a, b)

    plt.scatter(x_array, y_array, marker=marker[i], color="gray", label=f"V = {VGSarray[i]}")
    plt.plot(x_array, y_array, linestyle=linestyle[i], color="black", label=f"V = {VGSarray[i]}")
 

drain_plot(drain_0, 0)
drain_plot(drain_0245, 1)
drain_plot(drain_1, 2)

plt.xlabel(r"$V_{DS}$ ($V$)")
plt.ylabel(r"$I_{D}$ ($mA$)")
plt.title("Drain Characterstics of p-channel JFET")

plt.grid()
plt.legend()
plt.savefig("plots/drain_plot.png")
#plt.clf()
plt.show()









# Create a nice table
#table_df = pd.DataFrame({
#    "\\#": [i+1 for i in range(len(curr_inc))],
#    "Current I (A)": curr_inc,
#    "Magnetic Field B (10G)": field_inc,
#    "B$^2$ (G$^2$)": (np.array(field_inc)*10)**2,
#})

#save_latex_table(table_df, f"Calibration Data (Increasing Current)", f"tab:calib_inc", CALIB_TABLES_FILE)





