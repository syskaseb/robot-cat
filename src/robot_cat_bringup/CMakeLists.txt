cmake_minimum_required(VERSION 3.16)
project(robot_cat_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
