"""Bring up the Gazebo *server*, spawn the cat, and start control.

The GUI is deliberately NOT launched here. On macOS, Cocoa requires window
creation on the main thread, so ``gz sim`` must be split into a server process
and a GUI process. Run the GUI separately::

    gz sim -g          # or: ./run/gui.sh

Everything else - robot_state_publisher, the spawn, all four controllers and
the gait node - is started here in the right order.
"""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    description_share = get_package_share_directory("robot_cat_description")

    xacro_file = os.path.join(description_share, "urdf", "cat.urdf.xacro")
    controllers_file = os.path.join(description_share, "config", "controllers.yaml")

    use_sim_time = LaunchConfiguration("use_sim_time")
    spawn_height = LaunchConfiguration("spawn_height")
    start_gait = LaunchConfiguration("start_gait")
    world = LaunchConfiguration("world")
    scale = LaunchConfiguration("scale")
    mass_scale = LaunchConfiguration("mass_scale")

    args = [
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument(
            "spawn_height",
            default_value="0.20",
            description="Drop height. Must clear the stance height so the cat "
            "does not spawn with its paws inside the floor.",
        ),
        DeclareLaunchArgument(
            "start_gait",
            default_value="true",
            description="Set false to drive /leg_position_controller/commands "
            "by hand instead of running the gait node.",
        ),
        DeclareLaunchArgument(
            "scale",
            default_value="1.0",
            description="Body size multiplier, applied to the model and the "
            "gait together. 1.0 is already a real domestic cat - 24.2 cm at "
            "the withers, 3.7 kg - so leave it alone unless you want a "
            "different animal. 1.87 is what 'about 50 cm tall' works out to, "
            "and weighs 24 kg. This picks an actuator class, not a look: "
            "about 5 Nm per joint against 27 Nm.",
        ),
        DeclareLaunchArgument(
            "mass_scale",
            default_value="1.0",
            description="Construction weight, independent of size. 1.0 keeps "
            "the geometric scale^3 mass; 0.62 models a hollow frame at the "
            "same dimensions, which is roughly what Unitree's Go2 weighs for "
            "its size. Torque tracks mass nearly linearly in a slow walk.",
        ),
        DeclareLaunchArgument(
            "world",
            default_value="cat_world.sdf",
            description="World file name, looked up under "
            "robot_cat_bringup/worlds/. Try apartment_world.sdf for a living "
            "room + kitchen the cat can walk around in.",
        ),
    ]

    world_file = PathJoinSubstitution(
        [FindPackageShare("robot_cat_bringup"), "worlds", world]
    )

    # ParameterValue(..., value_type=str) is required: without it launch tries
    # to YAML-parse the URDF and dies on the first colon.
    robot_description = ParameterValue(
        Command(
            ["xacro ", xacro_file, " use_gazebo:=true scale:=", scale, " mass_scale:=", mass_scale,
             " controllers_file:=", controllers_file]
        ),
        value_type=str,
    )

    # -- Gazebo server (headless). -r starts unpaused. --------------------
    gz_server = ExecuteProcess(
        cmd=["gz", "sim", "-r", "-s", "-v", "2", world_file],
        output="screen",
    )

    # -- /clock from Gazebo, so every ROS node shares simulation time. ----
    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {"robot_description": robot_description, "use_sim_time": use_sim_time}
        ],
    )

    # -- Spawn from the /robot_description topic published above. ---------
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "/robot_description",
            "-name", "robot_cat",
            "-z", spawn_height,
            "-allow_renaming", "true",
        ],
    )

    # The controller_manager lives inside the Gazebo server, loaded by
    # gz_ros2_control along with the model - so it does not exist until the
    # spawn completes. Chain the spawners off the spawn process exiting.
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    leg_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["leg_position_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    head_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["head_position_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    tail_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["tail_position_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    gait = Node(
        package="robot_cat_gait",
        executable="gait_controller",
        output="screen",
        condition=IfCondition(start_gait),
        parameters=[{"use_sim_time": use_sim_time, "scale": scale}],
    )

    return LaunchDescription(
        args
        + [
            gz_server,
            clock_bridge,
            robot_state_publisher,
            spawn,
            RegisterEventHandler(
                OnProcessExit(target_action=spawn, on_exit=[joint_state_broadcaster])
            ),
            RegisterEventHandler(
                OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[leg_controller, head_controller, tail_controller],
                )
            ),
            RegisterEventHandler(
                OnProcessExit(target_action=leg_controller, on_exit=[gait])
            ),
        ]
    )
