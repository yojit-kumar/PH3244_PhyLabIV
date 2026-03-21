import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

sys.path.append("../lib/")
from latex_utils import *

run_before_start()

# --- CONFIGURATION & UNCERTAINTIES ---
C = 7.576e6

#DATA LOADING
ebm1 = pd.read_csv("data/ebm1.csv")
ebm2 = pd.read_csv("data/ebm2.csv")

save_latex_table(ebm1, f"First set of reading at 1 ampere", f"tab:ebm1", OBS_TABLES_FILE)
save_latex_table(ebm2, f"Second set of reading at 1.5 ampere", f"tab:ebm2", OBS_TABLES_FILE)

V_array1 = np.array(ebm1.iloc[:,0])
V_array2 = np.array(ebm2.iloc[:,0])

V_array = np.concatenate((V_array1, V_array2))

d_array1 = np.array(ebm1.iloc[:,3]) - np.array(ebm1.iloc[:,2])
d_array2 = np.array(ebm2.iloc[:,3]) - np.array(ebm2.iloc[:,2])

d_array = (np.concatenate((d_array1, d_array2)))*1e-2




## PLOTING
def linear_fit(x, a, b):
    return a*x + b

x_array = V_array1
y_array = (d_array1*1e-2)**2

params, covar = curve_fit(linear_fit, x_array, y_array)
a, b = params
a_err, b_err = np.sqrt(np.diag(covar))

save_latex_cmd("slopeOne", a)
save_latex_cmd("slopeOneerr", a_err)

result1 = C / a
result1err = result1 * a_err / a
save_latex_cmd("resultOne", result1)
save_latex_cmd("resultOneerr", result1err)


x_fit = np.linspace(min(x_array), max(x_array), 500)
y_fit = linear_fit(x_fit, a, b)

plt.scatter(x_array, y_array, color="black", label="Data")
plt.plot(x_fit, y_fit, color="black", label="Fit")

plt.xlabel(r"Voltage ($V$)")
plt.ylabel(r"$D^2$ m$^2$")
plt.title(r"Magnetizing Current $I = 1 A$")

plt.legend()
plt.grid()
plt.savefig("plots/ebm1.png")
#plt.show()
plt.clf()

x_array = V_array2
y_array = (d_array2*1e-2)**2

params, covar = curve_fit(linear_fit, x_array, y_array)
a, b = params
a_err, b_err = np.sqrt(np.diag(covar))

save_latex_cmd("slopeTwo", a)
save_latex_cmd("slopeTwoerr", a_err)

result2 = C / (a * (1.5)**2)
result2err = result2 * a_err / a
save_latex_cmd("resultTwo", result2)
save_latex_cmd("resultTwoerr", result2err)

x_fit = np.linspace(min(x_array), max(x_array), 500)
y_fit = linear_fit(x_fit, a, b)

plt.scatter(x_array, y_array, color="black", label="Data")
plt.plot(x_fit, y_fit, color="black", label="Fit")

plt.xlabel(r"Voltage ($V$)")
plt.ylabel(r"$D^2$ m$^2$")
plt.title(r"Magnetizing Current $I = 1.5 A$")

plt.legend()
plt.grid()
plt.savefig("plots/ebm2.png")
#plt.show()
plt.clf()


## DIRECT CALCULATION
I_array = np.repeat([1, 1.5],[6,6])
M_array = V_array/( (I_array)**2 * (d_array)**2 )
ebm_array = C * M_array

mean_ebm = np.mean(ebm_array)
std_ebm = np.std(ebm_array)
save_latex_cmd("meanEBM", mean_ebm)
save_latex_cmd("stdEBM", std_ebm)

analysis = pd.DataFrame({
    "\\#": [i+1 for i in range(len(V_array))],
    "Voltage (V)": V_array,
    "Current (A)": I_array,
    "Diameter (m2)": d_array,
    "V/I2d2": M_array,
    "e/m": ebm_array
})

save_latex_table(analysis, f"Directly calculated e/m ratio", f"tab:ebm", ANAL_TABLES_FILE)





