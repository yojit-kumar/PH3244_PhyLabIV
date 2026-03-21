# PH3244\_LabIV

This is a repository to just save and track my lab report and analysis for the 3rd year course in Physics Lab.

## Repository Structure

```
.
├── XX<_Experiment Name_>
│   ├── analysis.py
│   ├── data
│   │   ├── <_tables_>.tex
│   │   └── <_observations_>.csv
│   ├── manual
│   └── <_subfile_>.tex
│ 
├── lib
│   └── latex_utils.py
│       
├── main.pdf
├── main.tex
├── preamble.tex
└── README.md
```

We are using the `subfiles` LaTeX package to use a subdirectory structure to sort each experiment in a separate folder. The whole report can be compiled using the `main.tex` file.
