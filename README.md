# UOB High Flux Neutron Facility
**Author:** Max Conroy

This respository contains the starting neutron source files for use in OpenMC simulations of HF-ADNeF at the University of Birmingham.

### Input Card Method
These files are based off of MCNP input cards, where a C++ file is written for various incident proton energies.

### Compiled Source Method
This is a single C++ file that takes a proton energy as an input and samples initial neutron parameters from physical principles.
_Currently a work in progress._

### Installation
OpenMC will need to be installed on your system. This can be done via the instructions given here: https://docs.openmc.org/en/latest/quickinstall.html. I have manually built OpenMC from source using cmake.

You will also need to download the required cross section data for OpenMC, which can be found here: https://openmc.org/official-data-libraries/. The path to the cross_sections.xml file will need to be added to the PATH variable, which can be done by adding
```
export OPENMC_CROSS_SECTIONS="/home/<path_to_cross_section_data>/cross_sections.xml"
```
to your bashrc file.

To use the custom source files, they will need to be built with cmake as well. Specific instructions can be found in the relevant folders.

### Usage
If you use this code in your work, please reference it accordingly. I will be writing this up as part of my PhD and will update this github when that happens. Please contact me for more information at m.j.conroy@pgr.bham.ac.uk.
