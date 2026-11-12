# ECI150 Day 4: ROS 2 Practical (Student Guide)

**Duration:** 2 hours · **Platform:** The Construct (ROS 2 Humble ROSject) · **Robot of record:** UR5e

| Part | Topic | Time |
| --- | --- | --- |
| 1 | turtlesim, ROS 2 CLI, Python publisher/subscriber | 30 min |
| 2 | UR5e URDF in RViz and the TF tree | 25 min |
| 3 | UR5e in Gazebo Classic with ros2_control | 30 min |
| 4 | MoveIt 2 Panda demo: plan, execute, avoid obstacles | 35 min |

---

## Before you start (2 min)

Your instructor has already built the course workspace `~/eci150_ws`.

- **Terminals:** open them from The Construct **Shell / Terminal** tool. You will need **3 to 4 terminals**.
- **Windows (turtlesim, RViz, Gazebo):** these appear in The Construct **Graphical Tools** (web desktop). Keep it open.
- **In every new terminal**, run this first:

```bash
source ~/eci150_ws/install/setup.bash
```

Check that the course packages are visible:

```bash
ros2 pkg executables | grep eci150
```

✅ **You should see:**

```
eci150_moveit_demo add_collision_box
eci150_turtle_demo circle_publisher
eci150_turtle_demo pose_subscriber
eci150_ur_control send_joint_trajectory
```

> Stop a running program with **Ctrl+C** in its terminal.

> **Edited a file? Rebuild.** The workspace is built with a plain `colcon build`, which *copies* files into `install/`. After you edit **any** course file (Python, launch, or RViz config), rebuild that package and re-source before running it again. For example:
>
> ```bash
> cd ~/eci150_ws && colcon build --packages-select eci150_turtle_demo && source install/setup.bash
> ```

---

## Part 1: turtlesim and the ROS 2 graph (30 min)

**Key words.** A **node** is a running program. A **topic** is a named channel that nodes publish messages to or subscribe to. A **service** is a request/response call. A **parameter** is a setting stored inside a node.

### 1.1 Start turtlesim (Terminal 1)

```bash
ros2 run turtlesim turtlesim_node
```

✅ A blue window with a turtle opens in Graphical Tools.

*Optional (Terminal 2):* drive the turtle with your keyboard. Click inside that terminal first, then use the arrow keys.

```bash
ros2 run turtlesim turtle_teleop_key
```

### 1.2 Nodes and topics (Terminal 3)

```bash
ros2 node list
ros2 node info /turtlesim
ros2 topic list -t
```

Answer these from the output:

- What is the type of `/turtle1/cmd_vel`? Of `/turtle1/pose`? Of `/turtle1/color_sensor`?

```bash
ros2 topic echo /turtle1/pose            # Ctrl+C to stop
ros2 topic hz /turtle1/pose              # how fast does turtlesim publish?
ros2 topic echo /turtle1/color_sensor --once
ros2 interface show geometry_msgs/msg/Twist
```

Publish velocity commands from the CLI:

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```

✅ The turtle drives in circles. Press **Ctrl+C** to stop publishing.

### 1.3 Services

```bash
ros2 service list -t
ros2 interface show turtlesim/srv/Spawn
```

Try each of these, one at a time, and watch the window after each:

```bash
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 4, 'off': 0}"
ros2 service call /turtle1/teleport_absolute turtlesim/srv/TeleportAbsolute "{x: 5.5, y: 5.5, theta: 1.57}"
ros2 service call /clear std_srvs/srv/Empty
ros2 service call /kill turtlesim/srv/Kill "{name: 'turtle2'}"
ros2 service call /reset std_srvs/srv/Empty
```

> `'off'` must be in quotes. Without them, YAML reads it as the boolean *false*.

### 1.4 Parameters

```bash
ros2 param list /turtlesim
ros2 param get /turtlesim background_r
ros2 param set /turtlesim background_r 150
ros2 param set /turtlesim background_g 50
ros2 param set /turtlesim background_b 200
ros2 service call /clear std_srvs/srv/Empty    # repaint if the colour has not changed yet
```

✅ The background colour changes.

**Stop everything from Part 1** (Ctrl+C in every terminal) before you continue.

### 1.5 The course publisher and subscriber

Open the code and read the comments:
`eci150_turtle_demo/eci150_turtle_demo/circle_publisher.py` and `pose_subscriber.py`.
If you change either file, rebuild `eci150_turtle_demo` and re-source (see *Before you start*) before you launch.

Run all three nodes with one launch file (Terminal 1):

```bash
ros2 launch eci150_turtle_demo turtle_demo.launch.py
```

✅ **You should see:** the turtle draws a circle, and the terminal prints about one line per second:
`[pose_subscriber]: x= 6.01  y= 5.66  theta=+0.48 rad ...` with `x`, `y` and `theta` changing.

Change the publisher's parameters while it runs (Terminal 2):

```bash
ros2 node list                                      # /turtlesim, /circle_publisher, /pose_subscriber
ros2 param set /circle_publisher angular_z 0.5      # bigger circle
ros2 param set /circle_publisher linear_x 2.0       # faster
ros2 topic hz /turtle1/cmd_vel                      # about 2 Hz
```

Or relaunch with different values:

```bash
ros2 launch eci150_turtle_demo turtle_demo.launch.py linear_x:=2.0 angular_z:=0.8
```

**Checkpoint 1:** the turtle circles, the subscriber logs its pose, and you can name the topic types and the services you called. Stop with Ctrl+C.

---

## Part 2: UR5e in RViz and the TF tree (25 min)

**Key words.** A **URDF** describes the robot's links and joints. `robot_state_publisher` combines the URDF with `/joint_states` and publishes **TF**, the live tree of coordinate frames.

### 2.1 Visualise the UR5e (Terminal 1)

```bash
ros2 launch eci150_ur_bringup view_ur5e.launch.py
```

✅ RViz opens with the UR5e. A **Joint State Publisher** window with six sliders opens too.

- Move each slider: `shoulder_pan_joint`, `shoulder_lift_joint`, `elbow_joint`, `wrist_1_joint`, `wrist_2_joint`, `wrist_3_joint`.
- In RViz, check that **Fixed Frame** (Global Options) is `base_link`.
- In RViz, tick and untick the **TF** display to see every frame's axes.

### 2.2 Inspect the data (Terminal 2)

```bash
ros2 node list
ros2 topic echo /joint_states --once
ros2 run tf2_ros tf2_echo base_link tool0       # move a slider and watch the numbers change; Ctrl+C
```

### 2.3 Draw the TF tree

```bash
cd ~ && ros2 run tf2_tools view_frames          # listens for 5 s and then writes frames_<date>.pdf
ls ~/frames_*.pdf
```

Open the PDF from the file browser in The Construct IDE. If `rqt_tf_tree` is installed, you can also use the live viewer:

```bash
ros2 run rqt_tf_tree rqt_tf_tree
```

✅ **You should see:** one chain from `base_link` through `shoulder_link`, `upper_arm_link`, `forearm_link`, `wrist_1_link`, `wrist_2_link`, `wrist_3_link`, and `flange` to `tool0`. You will also see a `world` frame above `base_link` and a few small side frames such as `base` and `ft_frame`.

**Questions:** Which joint moves the most links? Which frame does a tool get mounted on?

### 2.4 Optional: the Panda

Stop the UR5e launch (Ctrl+C), then:

```bash
ros2 launch eci150_ur_bringup view_panda.launch.py
```

Fixed Frame is `panda_link0`. Compare the 7 Panda arm joints with the 6 UR5e joints.

**Checkpoint 2:** the arm moves with the sliders, and you can show the chain from `base_link` to `tool0`. **Stop all Part 2 programs.**

---

## Part 3: UR5e in Gazebo Classic with ros2_control (30 min)

**Key words.** **Gazebo** simulates physics. **ros2_control** connects controllers to the (simulated) motors. The **joint_trajectory_controller** follows a list of timed joint positions. You send it an **action goal**: it accepts the goal, moves the arm, and reports a result.

### 3.1 Launch the simulation (Terminal 1)

```bash
ros2 launch eci150_ur_bringup ur5e_gazebo.launch.py
```

If the session is slow, run without the Gazebo window (RViz still shows the robot):

```bash
ros2 launch eci150_ur_bringup ur5e_gazebo.launch.py gazebo_gui:=false
```

✅ The UR5e stands upright in an empty Gazebo world. RViz opens a few seconds later. **Wait about 20 to 30 seconds** for the controllers to load.

### 3.2 Check the controllers (Terminal 2)

```bash
ros2 control list_controllers
ros2 action list
ros2 topic list | grep joint
```

✅ **You should see:** `joint_state_broadcaster` and `joint_trajectory_controller` both **active**, and the action `/joint_trajectory_controller/follow_joint_trajectory`.

### 3.3 Move the arm from the CLI

Send an action goal (all six joints in this order, values in radians):

```bash
ros2 action send_goal /joint_trajectory_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], \
    points: [{positions: [-0.5, -1.4, 0.6, -1.6, -1.57, 0.0], time_from_start: {sec: 5}}]}}"
```

✅ The output shows `Goal accepted`, and about 5 s later `Goal finished with status: SUCCEEDED`. The arm moves in both Gazebo and RViz.

*Alternative:* publish the same kind of command to a topic. There is no result with this method:

```bash
ros2 topic pub --once /joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory \
  "{joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], \
    points: [{positions: [0.0, -1.57, 0.0, -1.57, 0.0, 0.0], time_from_start: {sec: 4}}]}"
```

Watch the joint values:

```bash
ros2 topic echo /joint_states --field position
```

> `/joint_states` may list the joints in a **different order** than the controller does. Always read the `name` list next to the `position` list.

### 3.4 Move the arm from Python

Read `eci150_ur_control/eci150_ur_control/send_joint_trajectory.py` first. Then run it:

```bash
ros2 run eci150_ur_control send_joint_trajectory
```

✅ **You should see:**

```
use_sim_time = True
Waiting for action server /joint_trajectory_controller/follow_joint_trajectory ...
  t=3 s -> [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
  t=7 s -> [0.6, -1.2, 0.9, -1.3, -1.57, 0.0]
Goal ACCEPTED - watch the arm move in Gazebo and RViz.
Goal SUCCEEDED.
```

The arm first returns upright, then pans and bends its elbow. The script exits by itself.

Send the arm back to upright only:

```bash
ros2 run eci150_ur_control send_joint_trajectory --ros-args -p home_only:=true
```

**Challenge:** edit `TEACHING_POSE` with small changes (keep them under about 0.5 rad), rebuild, and run again. Your edit has no effect until you rebuild:

```bash
cd ~/eci150_ws && colcon build --packages-select eci150_ur_control && source install/setup.bash
ros2 run eci150_ur_control send_joint_trajectory
```

**Checkpoint 3:** both controllers are active, your CLI goal succeeds, and the Python client's goal succeeds.

### ⚠️ Stop Gazebo now

Press Ctrl+C in **every** Part 3 terminal. Part 4 uses a different robot and must not share the session with Gazebo.

---

## Part 4: MoveIt 2 with the Panda (35 min)

**Key words.** **MoveIt** is a motion planner. You give it a goal, and it finds a collision-free path. The **planning scene** is MoveIt's model of the world, and **collision objects** are obstacles in it. This demo uses *mock* hardware, which is a perfect simulated controller with no physics.

### 4.1 Launch the demo (Terminal 1)

```bash
ros2 launch moveit_resources_panda_moveit_config demo.launch.py
```

✅ RViz opens with the Panda and a **MotionPlanning** panel. In the Displays panel, **Fixed Frame** is `panda_link0`.

### 4.2 Plan and execute

In **MotionPlanning → Planning** tab:

1. Check that **Planning Group** (in the **Query** box of the Planning tab) is `panda_arm`.
2. **Start State:** `<current>`. **Goal State:** `<random valid>` (or `ready` / `extended`).
   You can also drag the arrows and rings at the gripper (the interactive marker).
3. Click **Plan**. An animated "ghost" arm shows the path.
4. Click **Execute**. The arm moves.

Repeat 2 or 3 times with different goals.

### 4.3 Set up a sweep

Use the **Joints** tab to set exact goal joint values. If the tab shows degrees, use the values in brackets.

| Joint | Pose A | Pose B |
| --- | --- | --- |
| panda_joint1 | **-0.8** (-45.8°) | **0.8** (45.8°) |
| panda_joint2 | 0.4 (22.9°) | 0.4 (22.9°) |
| panda_joint3 | 0.0 | 0.0 |
| panda_joint4 | -2.0 (-114.6°) | -2.0 (-114.6°) |
| panda_joint5 | 0.0 | 0.0 |
| panda_joint6 | 2.4 (137.5°) | 2.4 (137.5°) |
| panda_joint7 | 0.785 (45°) | 0.785 (45°) |

1. Set **Pose A**, then **Plan & Execute**. The gripper ends low, to the right of the robot.
2. Set **Pose B** and click **Plan**. Do not execute. Note the path: a low sweep straight across the front.

### 4.4 Add a box by hand in RViz

In **MotionPlanning → Scene Objects**:

1. Choose **Box** in the shape list, then click the green **+**.
2. Rename the object to `rviz_box` (double-click its name in the list).
3. Set its size to **0.15 × 0.15 × 0.40** and its position to **x = 0.40, y = 0.00, z = 0.20**.
4. If you see a **Publish** button, click it so that move_group receives the box.

Goal is still Pose B. Click **Plan** again.

✅ **You should see:** the new path lifts the gripper **over or around** the box instead of sweeping through it. If planning fails once, click **Plan** again.

Remove `rviz_box` (select it in the list and remove it), and Publish again if needed.

### 4.5 Add a box from Python (Terminal 2)

Read `eci150_moveit_demo/eci150_moveit_demo/add_collision_box.py`, then run:

```bash
ros2 run eci150_moveit_demo add_collision_box
```

✅ The terminal prints `Added "eci150_box" (0.15 x 0.15 x 0.4 m) at x=0.40 y=0.00 z=0.20 in panda_link0...`. A green box named `eci150_box` appears in RViz and in the Scene Objects list.

Plan to Pose B again and compare. Then **Execute**.

Remove the box and plan once more:

```bash
ros2 run eci150_moveit_demo add_collision_box --ros-args -p remove:=true
```

**Challenges:**

- Move the box: `ros2 run eci150_moveit_demo add_collision_box --ros-args -p box_x:=0.5 -p box_z:=0.3`. Does the path change?
- Put the goal **inside** the box. What does MoveIt report?

**Checkpoint 4:** Plan & Execute works, both boxes changed the plan, and `remove:=true` cleared `eci150_box`.

---

## If you get stuck, call a TA

Raise your hand (or post in chat) and tell the TA **which Part** you are on and **which symptom** you see:

| Symptom | Tell the TA |
| --- | --- |
| No window appears (turtlesim / RViz / Gazebo) | "GUI not showing" |
| `Package 'eci150_...' not found` / `ros2: command not found` | "workspace not sourced" |
| I edited a course file but nothing changed | "forgot to rebuild" (`colcon build --packages-select <pkg>`, then re-source) |
| `package 'gazebo_ros' not found` | "Gazebo Classic missing" |
| Gazebo very slow, arm falls over or "explodes" | "Gazebo unstable" |
| `list_controllers` empty or not *active*; action server not available | "controllers not active" |
| Action goal accepted but never finishes | "goal hangs (sim time?)" |
| RViz shows no robot, or "No transform from ..." | "RViz empty / fixed frame" |
| MoveIt Plan always fails | "planning fails" |

While you wait, try: `ros2 node list`, `ros2 control list_controllers`, and check the **Fixed Frame** in RViz.
