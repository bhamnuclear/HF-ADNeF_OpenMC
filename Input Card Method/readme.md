## HF-ADNeF Neutron Starting Source

### Instructions:
Each folder corresponds to a different proton energy that can be used in an OpenMC simulation.

The src folder contains the .cpp file which has been produced by converting MCNP input cards.

If you wish to use a specific energy, navigate to the required folder and run:

```cmake --S src --B build```

Then:

```cmake --build build```

You can then use the libsource.so file as a compiled starting source in an OpenMC simulation. See the examples folder for how it can be implemented.

For more information on using compiled sources, see the OpenMC documentation: https://docs.openmc.org/en/stable/usersguide/settings.html.

### Usage:
If you use this code in your work, please note that I (Max Conroy) am creating this and will be publishing it as part of my PhD. The code will be available at https://github.com/mconroy101 and written up in the future. If you could cite my work appropriately that would be much appreciated.
Please contact: m.j.conroy@pgr.bham.ac.uk for more details.


