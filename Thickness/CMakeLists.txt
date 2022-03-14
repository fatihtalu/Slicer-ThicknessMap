cmake_minimum_required(VERSION 3.13.4)

project(Thickness)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/Thickness")
set(EXTENSION_CATEGORY "Shape Analysis")
set(EXTENSION_CONTRIBUTORS "Muhammed Fatih Talu (Inonu University, Computer Science Department)")
set(EXTENSION_DESCRIPTION "With this plugin, a thickness map of a segmented 3D structure can be created.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/Thickness.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/Thickness/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ThicknessMapping)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
