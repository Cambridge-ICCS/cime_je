# Fork of CIME implementing FTorch within CESM

This fork of CIME (main README below) has been made by ICCS to facilitate the use
of the [FTorch library](https://github.com/Cambridge-ICCS/FTorch) (for coupling PyTorch
machine learning models to Fortran codes) from within CESM (the Community Earth
System Model).

It is based on the `maint-5.6` branch which is used to support CESM 2.


## Using within CESM

To use in CESM, first obtain a copy of CESM as described [here](https://github.com/ESCOMP/CESM)
and then modify the `Externals.cfg` to point at this repository and branch instead:
```
[cime]
branch = ftorch_forpy_cime
protocol = git
repo_url = https://github.com/Cambridge-ICCS/cime_je
local_path = cime
required = True
```

You will also need to have a copy of `libtorch`.
On Derecho this can be loaded with:
```
module load libtorch/2.1.2
```

You will then need to build the FTorch library locally on your system as described
[here](https://github.com/Cambridge-ICCS/FTorch).

Finally Modify `scripts/Tools/Makefile` line 567 to set the environment variable
`FTORCH_LOC` to the location of the FTorch library on your system.

You can then proceed to write Fortran code using FTorch and build CESM as normal.


# cime
Common Infrastructure for Modeling the Earth

CIME, pronounced “SEAM”, contains the support scripts (configure, build, run, test), data models, essential
utility libraries, a “main” and other tools that are needed to build a single-executable coupled Earth System Model.
CIME is available in a stand-alone package that can be compiled and tested without active prognostic components
but is typically included in the source of a climate model. CIME does not contain: any active components,
any intra-component coupling capability (such as atmosphere physics-dynamics coupling).

*cime* (pronounced: seem) is currently used by the
<a href="http://www2.cesm.ucar.edu">Community Earth System Model </a>
     (CESM) and the <a href="https://climatemodeling.science.energy.gov/projects/energy-exascale-earth-system-model">
Energy Exascale Earth System Model</a> (E3SM).

# Documentation

See <a href="http://esmci.github.io/cime">esmci.github.io/cime</a>

# Developers

## Lead Developers
Case Control System: Jim Edwards (NCAR), Jim Foucar (SNL)

MCT-based Coupler/Driver:  Mariana Vertenstein (NCAR), Robert Jacob (ANL)

Data Models:  Mariana Vertenstein (NCAR)

## Also Developed by
Alice Bertini (NCAR), Tony Craig (NCAR), Michael Deakin (SNL), Chris Fischer (NCAR), Steve Goldhaber (NCAR),
Erich Foster (SNL), Mike Levy (NCAR), Bill Sacks (NCAR), Andrew Salinger (SNL), Sean Santos (NCAR), Jason Sarich (ANL),
Andreas Wilke (ANL).

# Acknowledgements

CIME is jointly developed with support from the Earth System Modeling program of DOE's BER office and the CESM program
of NSF's Division of Atmospheric and Geospace Sciences.

# License

CIME is free software made available under the BSD License. For details see the LICENSE file.
