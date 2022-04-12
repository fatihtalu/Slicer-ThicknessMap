cmake_minimum_required(VERSION 3.13.4)

project(ThicknessMap)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/ThicknessMap")
set(EXTENSION_CATEGORY "Shape Analysis")
set(EXTENSION_CONTRIBUTORS "Muhammed Fatih Talu (Inonu University)")
set(EXTENSION_DESCRIPTION "Calculation bone thickness mapping")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ThicknessMap.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ThicknessMap/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ThicknessMap)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
