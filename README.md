# Cryogenic_Material_Properties
## Description
Compilation of material properties at cryogenic temperatures for use in design and testing of cryogenic systems.

This Git Repository will serve to store the RAW thermal conductivity and other material properties data, compiled from decades of published resources, and analysis tools (in Python) for streamlined use and analysis.

The repository is being actively developed by Dr. Nicholas Galitzki and graduate students at the University of Texas. 

## Organizational Structure
All current development exits within the 'thermal_conductivity' folder
```
thermal_conductivity
    - lib
        - SS304
            - plot files
            - fit.lh5
            - RAW
                - measurement1.csv
                - measurement2.csv ...
        - Other materials eventually
```

## Operation
Most users of this repository will only ever use the thermal_conductivity_compilation files, which they may then import into other programs. These files contain the multi-order fits to real thermal conductivity data collected over decades of research. 

For users who wish to adjust the fits, add more data, or investigate the 'behind the scenes' of this repository, it is encouraged to familiarize oneself with the 'thermal_conductivity_tutorial.ipynb' notebook in its entirety.
This notebook produces all of the plots and fits (and puts them in the appropriate folders).

The output of the notebook is a compiled csv and txt file with the thermal conductivity fit parameters for each material. 

## Fitting Method
The TC fits are produced by first fitting the low temperature data and the high temperature data separately. Then, the two fits are connected using an error function.

The final fit follows the following structure:
```
Log10(k) = Log10(T[a+bT+cT^2+...])*0.5*[1-ERF(15*(Log10(10T/erf_param)))]+[A+B*Log10(T)+C*(Log10(T))^2+D*(Log10(T))^3+...]*0.5*[1+ERF(15*(Log10(T/erf_param)))]
```

or in python form
```
    erf_low = 0.5*(1-erf(15*(np.log10(10*T/erf_param))))
    low_range = np.log10(np.abs(T*(low_fit(T))))
    erf_hi = 0.5*(1+erf(15*(np.log10(T/erf_param))))
    hi_range = (hi_fit(np.log10(T)))

    logk = low_range*erf_low+hi_range*erf_hi
    # logk = np.log10(np.abs(T*(low_fit(T))))*0.5*(1-erf(15*(np.log10(10*T/erf_param))))+(hi_fit(np.log10(T)))*0.5*(1+erf(15*(np.log10(T/erf_param))))
```