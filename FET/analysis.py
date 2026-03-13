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
    
    # Inject \resizebox around the tabular environment
    latex_str = latex_str.replace(
        "\\begin{tabular}", 
        "\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}"
    )
    latex_str = latex_str.replace(
        "\\end{tabular}", 
        "\\end{tabular}%\n}"
    )

    with open(FILE, "a") as f:
        f.write(latex_str + "\n\n")

#DATA LOADING
drain_0 = pd.read_csv("data/drain_0.csv")
drain_0245 = pd.read_csv("data/drain_0245.csv")
drain_1 = pd.read_csv("data/drain_1.csv")

transfer_2 = pd.read_csv("data/transfer_2.csv")
transfer_405 = pd.read_csv("data/transfer_405.csv")
transfer_602 = pd.read_csv("data/transfer_602.csv")

VGSarray = np.array([0.0, -0.245, -1.0])
VDSarray = np.array([2.0, 4.05, 6.02])

marker = ['o', 's', '^']
linestyle = ['-', ':', '-.']


####
# 1. Combine Drain DataFrames side-by-side
# axis=1 tells pandas to concatenate as columns, not rows
drain_combined = pd.concat([drain_0, drain_0245, drain_1], axis=1)

# Assign clear LaTeX column names for all 6 columns
drain_combined.columns = [
    r"$V_{DS}$ (V)", r"$I_D$ (mA) [$V_{GS}=0$]", 
    r"$V_{DS}$ (V)", r"$I_D$ (mA) [$V_{GS}=-0.245$]", 
    r"$V_{DS}$ (V)", r"$I_D$ (mA) [$V_{GS}=-1.0$]"
]

save_latex_table(
    drain_combined, 
    "Combined Drain Characteristics Observation Table", 
    "tab:drain_obs_combined", 
    OBS_TABLES_FILE
)

# 2. Combine Transfer DataFrames side-by-side
transfer_combined = pd.concat([transfer_2, transfer_405, transfer_602], axis=1)

# Assign clear LaTeX column names for all 6 columns
transfer_combined.columns = [
    r"$V_{GS}$ (V)", r"$I_D$ (mA) [$V_{DS}=2.0$]", 
    r"$V_{GS}$ (V)", r"$I_D$ (mA) [$V_{DS}=4.05$]", 
    r"$V_{GS}$ (V)", r"$I_D$ (mA) [$V_{DS}=6.02$]"
]

save_latex_table(
    transfer_combined, 
    "Combined Transfer Characteristics Observation Table", 
    "tab:transfer_obs_combined", 
    OBS_TABLES_FILE
)
######


def linear_fit(x, a, b):
    return a*x + b

def drain_plot(dataFrame, i):
    x_array = np.array(dataFrame.iloc[:,0])*(-1)
    y_array = np.array(dataFrame.iloc[:,1])*(-1)

    #x_fit = x_array[-7:]
    #y_fit = y_array[-7:]

    #params, covar = curve_fit(linear_fit, x_fit, y_fit)
    #a, b = params

    #x_fit = np.linspace(np.min(x_fit), np.max(x_fit), 500)
    #y_fit = linear_fit(x_fit, a, b)

    plt.scatter(x_array, y_array, marker=marker[i], color="gray", label=f"V_GS = {VGSarray[i]}")
    plt.plot(x_array, y_array, linestyle=linestyle[i], color="black", label=f"V_GS = {VGSarray[i]}")
 

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


def transfer_plot(dataFrame, i):
    x_array = np.array(dataFrame.iloc[:,0])
    y_array = np.array(dataFrame.iloc[:,1])

    plt.scatter(x_array, y_array, marker=marker[i], color="gray", label=f"V_DS = {VDSarray[i]}")
    plt.plot(x_array, y_array, linestyle=linestyle[i], color="black", label=f"V_DS = {VDSarray[i]}")
 

transfer_plot(transfer_2, 0)
transfer_plot(transfer_405, 1)
transfer_plot(transfer_602, 2)

plt.xlabel(r"$V_{GS}$ ($V$)")
plt.ylabel(r"$I_{DSS}$ ($mA$)")
plt.title("Transfer Characterstics of p-channel JFET")

plt.grid()
plt.legend()
plt.savefig("plots/transfer_plot.png")
#plt.clf()
plt.show()

def drain_resistance_plot(dataFrame, i):
    x_array = np.array(dataFrame.iloc[:,0])*(-1)
    y_array = np.array(dataFrame.iloc[:,1])*(-1)

    x_fit = x_array[-7:]
    y_fit = y_array[-7:]

    params, covar = curve_fit(linear_fit, x_fit, y_fit)
    a, b = params
    a_err, b_err = np.sqrt(np.diag(covar))

    slope_name = ["slopeOne", "slopeTwo", "slopeThree"]
    slopeErr_name = ["slopeOneErr", "slopeTwoErr", "slopeThreeErr"]
    rd_name = ["rdOne", "rdTwo", "rdThree"]

    save_latex_cmd(slope_name[i], a)
    save_latex_cmd(slopeErr_name[i], a_err)
    rd = 1/a
    save_latex_cmd(rd_name[i], rd)

    x_fit = np.linspace(np.min(x_fit), np.max(x_fit), 500)
    y_fit = linear_fit(x_fit, a, b)

    plt.scatter(x_array, y_array, marker=marker[i], color="gray", label=f"V_GS = {VGSarray[i]}")
    plt.plot(x_fit, y_fit, linestyle=linestyle[i], color="black", label=f"slope = {a}")
 

drain_resistance_plot(drain_0, 0)
drain_resistance_plot(drain_0245, 1)
drain_resistance_plot(drain_1, 2)

plt.xlabel(r"$V_{DS}$ ($V$)")
plt.ylabel(r"$I_{D}$ ($mA$)")
plt.title("Drain Resistance of p-channel JFET")

plt.grid()
plt.legend()
plt.savefig("plots/drain_resistance_plot.png")
#plt.clf()
plt.show()

latex_vds_names = ["Two", "FourPointZeroFive", "SixPointZeroTwo"]

def transconductance_plot(dataFrame, i):
    x_array = np.array(dataFrame.iloc[:,0])
    y_array = np.array(dataFrame.iloc[:,1])

    # Calculate transconductance gm = d(I_D) / d(V_GS)
    gm_array = np.gradient(y_array, x_array)
    gm_array = np.abs(gm_array)

    # Plotting gm vs V_GS
    plt.scatter(x_array, gm_array, marker=marker[i], color="gray")
    plt.plot(x_array, gm_array, linestyle=linestyle[i], color="black", label=f"V_DS = {VDSarray[i]}")
    
    gm0 = np.max(gm_array)
    
    # Create a 100% alphabetical LaTeX command name
    cmd_name = f"gmZeroVDS{latex_vds_names[i]}" 
    save_latex_cmd(cmd_name, gm0)

# Clear the figure to ensure previous plots don't overlap
plt.clf()

transconductance_plot(transfer_2, 0)
transconductance_plot(transfer_405, 1)
transconductance_plot(transfer_602, 2)

plt.xlabel(r"$V_{GS}$ ($V$)")
plt.ylabel(r"$g_m$ ($mS$)")
plt.title("Transconductance ($g_m$) vs $V_{GS}$ of p-channel JFET")

plt.grid()
plt.legend()
plt.savefig("plots/transconductance_plot.png")
plt.show()


# Create a nice table
#table_df = pd.DataFrame({
#    "\\#": [i+1 for i in range(len(curr_inc))],
#    "Current I (A)": curr_inc,
#    "Magnetic Field B (10G)": field_inc,
#    "B$^2$ (G$^2$)": (np.array(field_inc)*10)**2,
#})

#save_latex_table(table_df, f"Calibration Data (Increasing Current)", f"tab:calib_inc", CALIB_TABLES_FILE)





