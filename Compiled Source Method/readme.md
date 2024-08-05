## HF-ADNeF Neutron Starting Source
This code is currently a WIP.
### Instructions:
The src folder contains the .cpp file which samples neutron starting conditions from physical principles and experimentally measured data.

To use the code, first compile it via:

```cmake --S src --B build```

Then:

```cmake --build build```

You can then use the libsource.so file as a compiled starting source in an OpenMC simulation. It requires a single parameter which is the energy of the proton beam incident upon the lithium target, which should be passed as a string. See the examples folder for how it can be implemented.

For more information on using compiled sources, see the OpenMC documentation: https://docs.openmc.org/en/stable/usersguide/settings.html.
