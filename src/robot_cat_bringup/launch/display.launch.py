"""Inspect the cat in RViz with no simulator involved.

Use this to check geometry and joint sign conventions: drag a slider in
joint_state_publisher_gui and watch which link moves which way. Much faster
than restarting Gazebo, and it isolates description bugs from physics bugs.
"""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    description_share = get_package_share_directory("robot_cat_description")
    bringup_share = get_package_share_directory("robot_cat_bringup")

    xacro_file = os.path.join(description_share, "urdf", "cat.urdf.xacro")
    rviz_config = os.path.join(bringup_share, "rviz", "cat.rviz")

    # use_gazebo:=false drops the ros2_control and plugin blocks, which RViz
    # neither needs nor understands.
    robot_description = ParameterValue(
        Command(["xacro ", xacro_file, " use_gazebo:=false"]), value_type=str
    )

    return LaunchDescription(
        [
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": robot_description}],
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                output="screen",
                arguments=["-d", rviz_config],
            ),
        ]
    )
