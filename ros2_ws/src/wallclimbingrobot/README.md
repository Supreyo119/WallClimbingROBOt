# Wall climbing robot — ROS 2 Jazzy / Gazebo Harmonic

From `~/ros2_ws` (the source package is in the nested `ros2_ws/src` directory):

```bash
source /opt/ros/jazzy/setup.bash
colcon build --base-paths ros2_ws/src --packages-select wallclimbingrobot
source install/setup.bash
ros2 launch wallclimbingrobot gazebo.launch.py
# Without a GUI: append gui:=false
```

The red robot starts attached to the x=0 face of a 3 m wide, 4 m high wall,
0.65 m above the floor, with its forward axis pointing upward. The central
fan spins and defaults to full power. Wheel cylinders replace CAD wheel
exports containing extraneous chassis geometry; the rear-left axle rotation
is corrected to match the other wheels. The chassis retains its CAD visual.

The launch automatically climbs between 0.65 and 2.7 m, reversing at each
height using actual Gazebo pose feedback. Launch with `demo:=false` for
manual controls; the demo would otherwise overwrite manual velocity and fan commands.

In another terminal, source the same setup files, then:

```bash
# Climb (positive forward velocity is upward on the wall)
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.1}}'
# Stop (commands persist until replaced)
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{}'
# Fan throttle, 0..1; zero releases adhesion and the robot can fall
ros2 topic pub --once /fan_speed std_msgs/msg/Float64 '{data: 1.0}'
```

## Adhesion approximation

`src/fan_adhesion.cpp` applies a force toward the wall at the chassis center.
It uses pressure deficit `dp = 0.5 * rho * (90 * throttle)^2 * 0.8`, with
rho=1.225 kg/m³ and an effective circular area of radius 0.09 m. Full-power
force is approximately 101 N. These are illustrative parameters, not
measured fan performance. A fan-driven pressure deficit depends on ducting,
leakage, gap, and fan curves; Bernoulli alone does not establish a real
robot's available suction. This is a lumped force model, not CFD.

Force only applies near the defined wall, with the underside facing it.
The nominal body-to-wall distance is 97 mm. A 20 mm additional gap loses
the seal linearly. No adhesion is applied outside the wall bounds or when
the chassis tilts too far away. Gravity remains enabled, and wheel-wall
friction produces climbing traction. The seal and chassis collision are
simplified; there is no floor-to-wall transition controller.

Validated: package builds, robot holds on the wall, and a 0.1 m/s forward
command produced approximately 0.575 m rise in a five-second wall-clock test
while x remained approximately -0.097 m. The simulation was then stopped
with a zero velocity command, leaving fan suction active.
