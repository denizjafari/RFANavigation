cmake_minimum_required(VERSION 2.8.9)

project(RFNavigation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/RFNavigation")
set(EXTENSION_CATEGORY "RFNavigation")
set(EXTENSION_CONTRIBUTORS "Deniz Jafari (SRI)")
set(EXTENSION_DESCRIPTION "This is an extension made for the rf probe project.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/RFNavigation.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/RFNavigation/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(TreatmentMaker)
add_subdirectory(TreatmentPlanReader)
add_subdirectory(DataToolRegistration)
add_subdirectory(ToolTracking)
add_subdirectory(TreatmentVisualization)
add_subdirectory(ImageRegistration)
add_subdirectory(RFANavWorkflow)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
