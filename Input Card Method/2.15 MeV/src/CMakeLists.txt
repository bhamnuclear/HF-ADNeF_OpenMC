cmake_minimum_required(VERSION 3.3 FATAL_ERROR)               
project(openmc_sources CXX)
add_library(source SHARED Li_source_Epmin_0_Epmax_2.15.cpp)
find_package(OpenMC REQUIRED HINTS $ENV{CONDA_PREFIX}/lib64/cmake/OpenMC)               
target_link_libraries(source OpenMC::libopenmc)