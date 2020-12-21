cmake_minimum_required(VERSION 3.13.4)

project(VolumeSwitcher)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/VolumeSwitcher")
set(EXTENSION_CATEGORY "Utilities")
set(EXTENSION_CONTRIBUTORS "Filippo Maria Castelli (European Laboratory for NonLinear Spectroscopy)")
set(EXTENSION_DESCRIPTION "Volume Switcher lets you change volumes while maintaining zoom and 3D position of the views.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/VolumeSwitcher.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/VolumeSwitcher/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(VolumeSwitcher)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
