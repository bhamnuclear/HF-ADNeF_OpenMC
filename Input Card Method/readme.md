## HF-ADNeF Neutron Starting Source

### Instructions:
Each folder corresponds to a different proton energy that can be used in an OpenMC simulation.

The src folder contains the .cpp file which has been produced by converting MCNP input cards.

If you wish to use a specific energy, navigate to the required folder and run:

```cmake -S src -B build```

Then:

```cmake --build build```

You can then use the libsource.so file as a compiled starting source in an OpenMC simulation. See the examples folder for how it can be implemented.

For more information on using compiled sources, see the OpenMC documentation: https://docs.openmc.org/en/stable/usersguide/settings.html.

### Usage:
If you use this code in your work, please note that I (Max Conroy) will be publishing it as part of my PhD. The code will be available at this github and written up in the future. If you could cite my work appropriately that would be much appreciated.
Please contact: m.j.conroy@pgr.bham.ac.uk for more details.


### References:
These source files are adapted from the following work:

1) Minsky, D. M., Kreiner, A. J., & Valda, A. A. (2011). AB-BNCT beam shaping assembly based on 7Li(p,n)7Be reaction optimization. Applied Radiation and Isotopes, 69(12), 1668–1671. https://doi.org/10.1016/J.APRADISO.2011.02.047
