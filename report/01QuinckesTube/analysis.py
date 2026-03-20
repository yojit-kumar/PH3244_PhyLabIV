import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



# --- CONFIGURATION & UNCERTAINTIES ---

ERR_CURRENT = 0.01      
ERR_FIELD = 10.0        
ERR_MICROSCOPE = 0.01   

# Constants for Chi Calculation
DENSITY_SOL = 1280   #kg/m^3      
GRAVITY = 9.8          # m/s^2
MU_0 = 4 * np.pi * 1e-7 # T*m/A

# File to save LaTeX commands/tables
RESULTS_FILE = "data/calculated_results.tex"
CALIB_TABLES_FILE = "data/calibration_tables.tex"
MEASU_TABLES_FILE = "data/measurement_tables.tex"

# Open files to clear them/start fresh
with open(RESULTS_FILE, "w") as f:
    f.write("")
with open(CALIB_TABLES_FILE, "w") as f:
    f.write("% Auto-generated tables from analysis.py\n")
with open(MEASU_TABLES_FILE, "w") as f:
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


## --- CALIBRATION --- ##

#DATA LOADING
calib_inc = pd.read_csv('data/calibration_increasing.csv')
calib_dec = pd.read_csv('data/calibration_decreasing.csv')

curr_inc = calib_inc['current'].values
curr_dec = calib_dec['current'].values
field_inc = calib_inc['magnetic_field'].values
field_dec = calib_dec['magnetic_field'].values

#FIT EQUATION
def quadratic(x, a, b, c):
    return a*x**2 + b*x + c

# INCREASE PLOT
x_array = np.array(curr_inc)
y_array = np.array(field_inc) * 10

params, covar = curve_fit(quadratic, x_array, y_array)
a, b, c = params
a_err, b_err, c_err = np.sqrt(np.diag(covar))

# Save Fit Parameters to LaTeX
save_latex_cmd(f"incA", a)
save_latex_cmd(f"incB", b)
save_latex_cmd(f"incC", c)

print(f"{a:.2f}, {b:.2f}, {c:.2f}")
print(f"{a_err:.2f}, {b_err:.2f}, {c_err:.2f}")

x_smooth = np.linspace(min(x_array), max(x_array), 500)
y_smooth = quadratic(x_smooth, a, b, c)

def inc_field(x_smooth, a=a, b=b, c=c):
    return quadratic(x_smooth, a, b, c)

plt.scatter(x_array, y_array, color='black', alpha=0.8)
plt.plot(x_smooth, y_smooth, color='black', alpha=0.5)

plt.xlabel("Current (in A)")
plt.ylabel("Magnetic Field (in Gauss)")
plt.title("Calibration Curve for Increasing Current")
#plt.legend()
plt.grid()
plt.savefig(f"plots/calibration_increasing.png")
plt.show()

# Create a nice table
table_df = pd.DataFrame({
    "\\#": [i+1 for i in range(len(curr_inc))],
    "Current I (A)": curr_inc,
    "Magnetic Field B (10G)": field_inc,
    "B$^2$ (G$^2$)": (np.array(field_inc)*10)**2,
})

save_latex_table(table_df, f"Calibration Data (Increasing Current)", f"tab:calib_inc", CALIB_TABLES_FILE)

# DECREASE PLOT
x_array = np.array(curr_dec)
y_array = np.array(field_dec) * 10

params, covar = curve_fit(quadratic, x_array, y_array)
a, b, c = params
a_err, b_err, c_err = np.sqrt(np.diag(covar))

# Save Fit Parameters to LaTeX
save_latex_cmd(f"decA", a)
save_latex_cmd(f"decB", b)
save_latex_cmd(f"decC", c)

print(f"{a:.2f}, {b:.2f}, {c:.2f}")
print(f"{a_err:.2f}, {b_err:.2f}, {c_err:.2f}")

x_smooth = np.linspace(min(x_array), max(x_array), 500)
y_smooth = quadratic(x_smooth, a, b, c)

def dec_field(x_smooth, a=a, b=b, c=c):
    return quadratic(x_smooth, a, b, c)

plt.scatter(x_array, y_array, color='black', alpha=0.8)
plt.plot(x_smooth, y_smooth, color='black', alpha=0.5)

plt.xlabel("Current (in A)")
plt.ylabel("Magnetic Field (in Gauss)")
plt.title("Calibration Curve for Decreasing Current")
#plt.legend()
plt.grid()
plt.savefig(f"plots/calibration_decreasing.png")
plt.show()

# Create a nice table
table_df = pd.DataFrame({
    "\\#": [i+1 for i in range(len(curr_dec))],
    "Current I (A)": curr_dec,
    "Magnetic Field B (10G)": field_dec,
    "B$^2$ (G$^2$)": (np.array(field_dec)*10)**2,
})

save_latex_table(table_df, f"Calibration Data (Decreasing Current)", f"tab:calib_dec", CALIB_TABLES_FILE)

########################################################




# --- MAIN READING --- #

#DATA LOADING
sol1_inc = pd.read_csv('data/sol1_reading_increasing.csv')
sol1_dec = pd.read_csv('data/sol1_reading_decreasing.csv')

sol2_inc = pd.read_csv('data/sol2_reading_increasing.csv')
sol2_dec = pd.read_csv('data/sol2_reading_decreasing.csv')


def convertor(reading, field):
    Height = reading["Reading"].values
    Height_diff = Height - min(reading["Reading"].values)
    Current = reading['Current'].values
    Field = field(np.array(Current))
    return Height, Height_diff, Current, Field

def linear(x, a, b):
    return a*x + b

def plot_reading(reading, field, label_name):
    Height, Height_diff, Current, Field = convertor(reading, field)

    x_array = (Field * 1e-4)**2
    y_array = Height_diff/1000
    
    params, covar = curve_fit(linear, x_array, y_array)
    a, b = params
    a_err, b_err = np.sqrt(np.diag(covar))
    
    print("a,b")
    print(f"{a:.2e}, {b:.2e}")
    print(f"{a_err:.2e}, {b_err:.2e}")

    ##############
    chi = (2 * DENSITY_SOL * GRAVITY * a) *MU_0
    chi_err = chi * (a_err/a) 

    print("chi")
    print(f"{chi:.2e}")
    print(f"{chi_err:.2e}")

    clean_name = label_name.replace(" ", "")
    save_latex_cmd(f"chi{clean_name}", chi)
    save_latex_cmd(f"chiErr{clean_name}", chi_err)
    save_latex_cmd(f"slope{clean_name}", a)
    save_latex_cmd(f"slopeErr{clean_name}", a_err)
    #####################

    x_smooth = np.linspace(min(x_array), max(x_array), 500)
    y_smooth = linear(x_smooth, a, b)

    plt.scatter(x_array, y_array, color='black', alpha=0.8)
    plt.plot(x_smooth, y_smooth, color='black', alpha=0.5)

    plt.xlabel(r"B$^2$ (in T$^2$)")
    plt.ylabel("Microscope Height Difference (in m)")
    plt.title(f"Quincke's Method: {label_name}")
    
    plt.grid()
    plt.savefig(f"plots/reading_{clean_name}.png")
    plt.show()

    res_table = pd.DataFrame({
        "\\#": [i+1 for i in range(len(Current))],
        "Current (A)": Current,
        "Field (G)": Field,
        "Readings (in mm)": Height,
        "Height Difference (in mm)": Height_diff
        })
    save_latex_table(res_table, f"Microscope Readings for {label_name}", f"tab:{clean_name}", MEASU_TABLES_FILE)



readings = [sol1_inc, sol1_dec, sol2_inc, sol2_dec]
fields = [inc_field, dec_field, inc_field, dec_field]
names_list = ["SolOne Inc", "SolOne Dec", "SolTwo Inc", "SolTwo Dec"]

for i, x in enumerate(readings):
    reading = x
    field = fields[i]
    plot_reading(reading, field, names_list[i])
