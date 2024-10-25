## HF-ADNeF Neutron Starting Source
This code can be used as a starting source term for neutrons produced via the <sup>7</sup>Li(p,n)<sup>7</sup>Be reaction, which is the production method at HF-ADneF.

For full details of how the code works, please see *document to be uploaded*.

In brief:
- Neutrons are produced uniformly in x and y over a 5-cm-radius disk, centred at y = -42 cm. This is to align with the proton beamline in CAD models of the facility.
- The z position of the neutron production depends on energy loss calculated from SRIM and the total cross section of the interaction. Near threshold, this uses the description given by Lee and Zhou [^1] and above this energy, experimental data from EXFOR are used.
- The emission vector of the neutrons is sampled from the differential cross section data given by Liskien and Paulsen [^2].
- The neutrons are given a weight such that tally results are per mC of proton current.

### Instructions:
The src folder contains the .cpp file which samples neutron starting conditions from physical principles and experimentally measured data.

To use the code, first compile it via:

```cmake -S src -B build```

Then:

```cmake --build build```

You can then use the libsource.so file as a compiled starting source in an OpenMC simulation. It requires a single parameter which is the energy of the proton beam incident upon the lithium target, which should be passed as a string. See the examples folder for how it can be implemented.

For more information on using compiled sources, see the OpenMC documentation: https://docs.openmc.org/en/stable/usersguide/settings.html.

### References:
[^1]: C. L. Lee and X. L. Zhou. “Thick target neutron yields for the 7Li(p,n)7Be reaction near threshold”. In: Nuclear Instruments and Methods in Physics Research Section B: Beam Interactions with Materials and Atoms 152.1 (Apr. 1999), pp. 1–11. issn: 0168-583X. doi: 10.1016/S0168-583X(99)00026-9.
[^2]: Horst Liskien and Arno Paulsen. “Neutron production cross sections and energies for the reactions 7Li(p,n)7Be and 7Li(p,n)7Be*”. In: Atomic Data and Nuclear Data Tables 15.1 (Jan. 1975), pp. 57–84. issn: 0092-640X. doi: 10.1016/0092-640X(75)90004-2.