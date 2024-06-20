cmake_minimum_required (VERSION 2.6)
project (spotting_algorithm)
add_library (SpottingAlgorithm MODULE gesturespotting.c mathcontext.c movementdetection.c templatematching.c)
#set_target_properties (SpottingAlgorithm
#	PROPERTIES
#		LIBRARY_OUTPUT_DIRECTORY_RELEASE ..
#)
