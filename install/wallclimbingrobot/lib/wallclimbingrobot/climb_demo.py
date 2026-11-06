#!/usr/bin/env python3
"""Drive between wall heights using Gazebo's actual model pose feedback."""
import time
import re
import subprocess
from types import SimpleNamespace
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


class ClimbDemo(Node):
    def __init__(self):
        super().__init__('climb_demo')
        self.command = self.create_publisher(Twist, '/cmd_vel', 10)
        self.fan = self.create_publisher(Float64, '/fan_speed', 10)
        self.declare_parameter("speed", 0.30)
        self.speed = abs(float(self.get_parameter("speed").value))
        self.direction = 1
        self.pose = None
        self.last_pose = 0.0
        self.create_timer(0.3, self.update)
        self.get_logger().info('Automatic wall climb: 0.65 to 2.7 metres. Disable with demo:=false.')

    def update(self):
        command = Twist()
        try:
            # Pose_V -> TFMessage drops model names in this bridge version.
            # Read the named Gazebo pose directly rather than guessing an index.
            result = subprocess.run(
                ['gz', 'topic', '-e', '-t', '/world/robot_world/pose/info', '-n', '1'],
                capture_output=True, text=True, timeout=1.0, check=True)
            block = result.stdout.split('name: "wallclimbingrobot"', 1)[1].split('orientation', 1)[0]
            values = {k: float(v) for k, v in re.findall(r'\b(x|y|z): ([\deE+.-]+)', block)}
            self.pose = SimpleNamespace(**{k: values.get(k, 0.0) for k in ('x', 'y', 'z')})
            self.last_pose = time.monotonic()
        except (subprocess.SubprocessError, IndexError, ValueError):
            self.pose = None
        self.fan.publish(Float64(data=1.0))
        if self.pose is not None and time.monotonic() - self.last_pose < 1.0:
            p = self.pose
            if abs(p.x + 0.097) < 0.025 and abs(p.y) < 1.0 and 0.35 < p.z < 3.2:
                if p.z >= 2.7:
                    self.direction = -1
                elif p.z <= 0.65:
                    self.direction = 1
                command.linear.x = self.speed * self.direction
        self.command.publish(command)


def main():
    rclpy.init()
    node = ClimbDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.command.publish(Twist())
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
