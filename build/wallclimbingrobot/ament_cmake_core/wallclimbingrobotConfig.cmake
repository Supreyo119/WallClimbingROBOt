# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_wallclimbingrobot_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED wallclimbingrobot_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(wallclimbingrobot_FOUND FALSE)
  elseif(NOT wallclimbingrobot_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(wallclimbingrobot_FOUND FALSE)
  endif()
  return()
endif()
set(_wallclimbingrobot_CONFIG_INCLUDED TRUE)

# output package information
if(NOT wallclimbingrobot_FIND_QUIETLY)
  message(STATUS "Found wallclimbingrobot: 1.0.0 (${wallclimbingrobot_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'wallclimbingrobot' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT wallclimbingrobot_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(wallclimbingrobot_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${wallclimbingrobot_DIR}/${_extra}")
endforeach()
