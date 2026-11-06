cmake_minimum_required(VERSION 3.5)
project(wallclimbingrobot)

# Default C++ standard
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

# Find ROS2 packages
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(robot_state_publisher REQUIRED)

# Install folders
install(DIRECTORY urdf meshes launch config worlds
  DESTINATION share/${PROJECT_NAME}
)

find_package(gz_sim_vendor REQUIRED)
find_package(gz-sim8 REQUIRED)
find_package(gz_plugin_vendor REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
add_library(fan_adhesion SHARED src/fan_adhesion.cpp)
target_link_libraries(fan_adhesion gz-sim8::gz-sim8 gz-plugin2::register)
install(TARGETS fan_adhesion LIBRARY DESTINATION lib)
install(PROGRAMS scripts/climb_demo.py DESTINATION lib/${PROJECT_NAME})
ament_package()