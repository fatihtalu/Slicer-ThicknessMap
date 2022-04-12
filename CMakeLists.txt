cmake_minimum_required(VERSION 3.13.4)

project(ThicknessMap)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/Thickness")
set(EXTENSION_CATEGORY "Shape Analysis")
set(EXTENSION_CONTRIBUTORS "Muhammed Fatih Talu (Inonu University, Computer Science Department)")
set(EXTENSION_DESCRIPTION "This extension can be installed in the 3d Slicer program. The purpose of this extension is to generate thickness maps of segments from MR or CT data. The thickness value of any desired point on the generated model can be obtained by using landmarks or the entire thickness map model can be exported to a file.")
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
