import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, DeclareLaunchArgument
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share = Path(get_package_share_directory('wallclimbingrobot'))
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('demo', default_value='true'),
        DeclareLaunchArgument('world', default_value=str(share / 'worlds/robot_world.sdf')),
        Node(package='wallclimbingrobot', executable='climb_demo.py', condition=IfCondition(LaunchConfiguration('demo')), output='screen'),
        SetEnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', os.path.join(get_package_prefix('wallclimbingrobot'), 'lib') + os.pathsep + os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', '')),
        SetEnvironmentVariable('QT_QPA_PLATFORM', 'xcb'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', str(share.parent) + os.pathsep + os.environ.get('GZ_SIM_RESOURCE_PATH', '')),
        ExecuteProcess(cmd=['gz', 'sim', '-s', '-r', LaunchConfiguration('world')], output='screen'),
        ExecuteProcess(cmd=['gz', 'sim', '-g'], condition=IfCondition(LaunchConfiguration('gui')), output='screen'),
        Node(package='robot_state_publisher', executable='robot_state_publisher', parameters=[{'robot_description': (share / 'urdf/Wallclimbingrobot.urdf').read_text(), 'use_sim_time': True}]),
        Node(package='ros_gz_sim', executable='create', arguments=['-name', 'wallclimbingrobot', '-topic', 'robot_description', '-x', '-0.098', '-z', '0.65', '-Y', '0', '-P', '-1.57079632679'], output='screen'),
        Node(package='ros_gz_bridge', executable='parameter_bridge', arguments=['/fan_speed@std_msgs/msg/Float64]gz.msgs.Double', '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock', '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist', '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry', '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V', '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'], output='screen'),
    ])
