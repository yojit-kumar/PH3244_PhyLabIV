RESULTS_FILE = "data/calculated_results.tex"
OBS_TABLES_FILE = "data/observation_tables.tex"
ANAL_TABLES_FILE = "data/analysis_tables.tex"

def run_before_start():
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

