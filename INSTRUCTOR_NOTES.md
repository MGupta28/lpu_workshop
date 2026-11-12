# ECI150 Day 4: Instructor Notes

Course designer: **Manan Gupta**. Host: **The Construct**, ROS 2 Humble ROSject only.
This lab is a ROS 2 practical. It is not a digital-twin or virtual-commissioning exercise.

---

## 1. Before class (do this the day before)

1. Create or duplicate a **ROS 2 Humble** ROSject on The Construct.
2. Clone the repo and run the setup script:

   ```bash
   mkdir -p ~/eci150_ws/src && cd ~/eci150_ws/src
   git clone <COURSE_REPO_URL> eci150_day4_lab
   bash ~/eci150_ws/src/eci150_day4_lab/scripts/setup_workspace.sh
   ```

   The script:
   - apt-installs the Classic 11 stack and the other lab packages: `gazebo_ros_pkgs`, `gazebo_ros2_control`, `ur_description`, `ur_controllers`, `ur_moveit_config`, MoveIt, the Panda resources, `turtlesim`, `tf2_tools`, and `rqt_tf_tree`.
   - Clones `Universal_Robots_ROS2_Gazebo_Simulation` (`humble` branch) into `src/`.
   - Runs `rosdep` and a plain `colcon build` (no `--symlink-install`, so the installed copy is always exactly what was last built).
   - Prints an OK/MISSING table.

   Options: set `ECI150_WS=/path` to use a different workspace, or `SKIP_APT=1` if you have no sudo. The script clones `ur_description` from source if its binary is missing.
3. Rehearse Parts 1 to 4 once in the ROSject. **Part 3 is the one that can fail on the platform** (see §6).
4. Share the ROSject with students so they get the pre-built workspace and do not have to build anything in class.

The student guide is `STUDENT_GUIDE.md`. Every student command assumes `source ~/eci150_ws/install/setup.bash`.

---

## 2. Suggested script and timing (120 min)

| Clock | Part | Instructor actions |
| --- | --- | --- |
| 0:00 to 0:02 | Setup | Open Terminal + Graphical Tools. Everyone runs `source ~/eci150_ws/install/setup.bash`. |
| 0:02 to 0:30 | **1** turtlesim | Demo `node list` → `topic list -t` → `topic echo` live (≈5 min). Students do 1.2 to 1.4 (≈15 min). Walk through `circle_publisher.py` on screen: Node, publisher, timer, parameter (≈3 min). Students run the launch file and `param set` (≈5 min). |
| 0:30 to 0:55 | **2** RViz / TF | Show the URDF → `robot_state_publisher` → TF flow on a whiteboard (3 min). Students jog the joints and run `view_frames`. Optional Panda viewer for fast students. |
| 0:55 to 1:25 | **3** Gazebo | Start the launch **first**, then explain while it loads (it takes 20 to 40 s on The Construct). Show `list_controllers`, run the CLI action goal, then the Python client. In the code, explain goal → accepted → result. |
| 1:25 | — | **Say out loud: "Ctrl+C every Part 3 terminal. Stop Gazebo before starting MoveIt."** Check with `ros2 node list` (should be empty). |
| 1:25 to 2:00 | **4** MoveIt | Demo Plan / Execute once. Students do random goals, then the Pose A → B sweep, add `rviz_box`, re-plan, then `add_collision_box`, re-plan, then `remove:=true`. |

If you are running late, cut the optional Panda viewer (2.4), the topic-pub alternative (3.3), and the Part 4 challenges.

---

## 3. Expected answers

### Part 1: CLI discoveries

| Kind | Name | Type |
| --- | --- | --- |
| Node | `/turtlesim` (+ `/teleop_turtle` if teleop runs; `/circle_publisher`, `/pose_subscriber` in 1.5) | |
| Topic | `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` |
| Topic | `/turtle1/pose` | `turtlesim/msg/Pose` (`x, y, theta, linear_velocity, angular_velocity`), ≈62 Hz |
| Topic | `/turtle1/color_sensor` | `turtlesim/msg/Color` (pixel colour **under** the turtle, so it shows the pen colour after `set_pen`) |
| Service | `/spawn` | `turtlesim/srv/Spawn` |
| Service | `/kill` | `turtlesim/srv/Kill` |
| Service | `/reset`, `/clear` | `std_srvs/srv/Empty` |
| Service | `/turtle1/set_pen` | `turtlesim/srv/SetPen` |
| Service | `/turtle1/teleport_absolute` | `turtlesim/srv/TeleportAbsolute` (also `teleport_relative`) |
| Parameter | `/turtlesim` `background_r`, `background_g`, `background_b` | int 0 to 255 (plus `use_sim_time`, `qos_overrides.*`) |

Course nodes:
- `circle_publisher` publishes `Twist` on `/turtle1/cmd_vel` at **2 Hz**. Its parameters are `linear_x` (1.0) and `angular_z` (1.0), and it reads them on every tick, so `ros2 param set` changes the motion live.
- `pose_subscriber` logs the pose at about **1 Hz** (`throttle_duration_sec=1.0`).

Circle radius = `linear_x / angular_z` (1.0 m by default).

### Part 2: TF tree (verified with `view_frames` on `ur_description` humble)

```
world → base_link → base_link_inertia → shoulder_link → upper_arm_link → forearm_link
      → wrist_1_link → wrist_2_link → wrist_3_link → flange → tool0
side leaves: base_link → base,  wrist_3_link → ft_frame
```

The path from `base_link` to `tool0` is a single chain. `world` is the root because `ur.urdf.xacro` fixes the robot to a `world` link. With all sliders at 0, `tf2_echo base_link tool0` gives about `[0.817, 0.233, 0.063]`, which is the arm stretched out horizontally. The upstream RViz config is `ur_description/rviz/view_robot.rviz` with Fixed Frame `base_link`. It was sufficient, so no custom `ur5e_view.rviz` is shipped.

Answers: `shoulder_pan_joint` moves every link after the base. Tools mount on `tool0` (the `flange` frame is the physical flange face).

### Part 3: trajectory used by `send_joint_trajectory.py`

One goal with two points. Joint order is `shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3` (rad):

| Point | `time_from_start` | Positions |
| --- | --- | --- |
| HOME (spawn pose, from `ur_description/config/initial_positions.yaml`) | 3 s | `[0.0, -1.57, 0.0, -1.57, 0.0, 0.0]` |
| TEACHING | 7 s | `[0.6, -1.2, 0.9, -1.3, -1.57, 0.0]` |

All values are far inside the UR5e limits (±2π for most joints, ±π for the elbow). The wrist stays about 0.67 m above the floor. Velocities are 0 at both points. `-p home_only:=true` sends only the HOME point.

The CLI goal in the guide is `[-0.5, -1.4, 0.6, -1.6, -1.57, 0.0]` over 5 s. The topic example returns to HOME over 4 s.

### Part 4: box used by `add_collision_box.py`

`id: eci150_box`, frame `panda_link0`, `BOX` 0.15 × 0.15 × 0.40 m at `x=0.40, y=0.00, z=0.20` (sits on the floor), identity orientation, `ADD`.
The node sends it as a `PlanningScene` diff through the **`/apply_planning_scene`** service and waits up to 30 s for the service. `-p remove:=true` sends the same id with `REMOVE`. `box_x`, `box_y`, and `box_z` are tuning parameters.

**Box tuning result.** With the brief's box pose, plans from `ready` to typical forward goals pass **over** the 0.40 m box, so the plan often does not change visibly. To guarantee a visible replan, the guide uses a low side-to-side sweep:

| | j1 | j2 | j3 | j4 | j5 | j6 | j7 | hand position (panda_link0) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pose A | -0.8 | 0.4 | 0 | -2.0 | 0 | 2.4 | 0.785 | (0.42, -0.44, 0.26) |
| Pose B | 0.8 | 0.4 | 0 | -2.0 | 0 | 2.4 | 0.785 | (0.42, 0.44, 0.26) |

I checked this offline with OMPL (`/plan_kinematic_path`, A → B, 5 attempts each):
- Without the box, the hand stays at z ≈ 0.26 m, a straight low sweep. 12 of 31 states on the direct joint path collide with the box.
- With the box, the hand is lifted to z ≈ 0.47 to 0.68 m. 4 of 5 attempts succeeded; one returned `INVALID_MOTION_PLAN`, so tell students to just press Plan again.

Make the goal infeasible on purpose: move the box onto Pose B (`-p box_y:=0.44 -p box_z:=0.2`). Planning then fails with a goal-in-collision message.

---

## 4. Differences from the brief, and things to know

| Item | What happened / decision |
| --- | --- |
| `ur5e_gazebo.launch.py` location | The brief's §6 table lists it under `eci150_ur_control`, but the §3 layout says `eci150_ur_bringup` holds the Parts 2 and 3 wrappers. It lives in **`eci150_ur_bringup`**. `eci150_ur_control` holds only the action client. |
| Including `view_ur.launch.xml` | On Humble, `XMLLaunchDescriptionSource` is in `launch_xml`, not in `launch.launch_description_sources`. The wrapper uses `AnyLaunchDescriptionSource`, which loads `.xml` (preferred) or falls back to `.py`. |
| `ur_simulation_gazebo` | It is **not on apt** for Humble (confirmed: there is no `ros-humble-ur-simulation-gazebo` candidate), so it is cloned from source. It `exec_depend`s on `ur_controllers` and `ur_moveit_config`, and the setup script apt-installs both. Its `ur_controllers.yaml` also declares UR-specific controllers, but only JSB and JTC are spawned. |
| `ur_description` | Binary `ros-humble-ur-description` exists (2.14.x at time of writing). The script falls back to a source clone. |
| `use_sim_time` | `send_joint_trajectory` **defaults to `use_sim_time:=true`** unless the user passes it, so students cannot forget it. `ur_sim_control.launch.py` already sets it on `robot_state_publisher`. Parts 1 and 4 use wall time. |
| `/joint_states` order | The broadcaster publishes the joints in a different order from the controller (for example `shoulder_pan, wrist_2, wrist_3, wrist_1, elbow, shoulder_lift` on mock hardware). The guide warns about this. |
| Panda viewer | There is no official view-only launch, so `view_panda.launch.py` assembles RSP + JSP-GUI + RViz from `moveit_resources_panda_description/urdf/panda.urdf` with `rviz/panda_view.rviz` (Fixed Frame `panda_link0`). |
| turtlesim background | On some builds the new colour shows only after the next repaint. The guide adds `ros2 service call /clear ...` as a fallback. |
| Build mode | The workspace uses a plain `colcon build`: every file (Python, launch, rviz) is **copied** into `install/`. Students must run `colcon build --packages-select <pkg>` and re-source after editing **any** course file, including Python. The guide says this in *Before you start*, Part 1.5, the Part 3 challenge, and the TA table ("forgot to rebuild"). |
| Robot for Part 4 / step 2.4 | Deliberately the **Panda**, as the brief requires (§2, §7: the upstream `moveit_resources_panda_moveit_config` demo with mock hardware). `ur_moveit_config` is installed only because `ur_simulation_gazebo` depends on it. Keeping the UR5e for Part 4 would be possible, but it would mean rewriting Part 4 against a different stack (`ur_moveit_config` + mock or Gazebo hardware) and re-tuning the box and poses. |
| Package maintainer | `Jon Doe <jon.doe@example.com>` in `package.xml`/`setup.py`. Course designer (docs) remains Manan Gupta. |
| `ur_robot_driver test_joint_trajectory_controller.launch.py` | Optional instructor-only demo. It is not installed by the script and not needed by students. |

### Verification status (what was actually run)

I ran the tests on a local Ubuntu 22.04 + Humble machine with no sudo, not on The Construct:

| Check | Result |
| --- | --- |
| `colcon build` of all 4 course packages + `ur_description` (source) + `ur_simulation_gazebo` | ✅ clean |
| `ros2 pkg executables` lists all 4 executables (format `<package> <executable>`, as in the guide). `flake8 --max-line-length 99` is clean. | ✅ |
| Part 1 launch | ✅ 3 nodes, `cmd_vel` at 2.000 Hz, pose logged ≈1 Hz. All services, topics, and params above confirmed. |
| Part 2 `view_ur5e` / `view_panda` | ✅ nodes up, `/joint_states` published, TF chain as above |
| Part 3 action client + CLI action + topic pub | ✅ against a real `joint_trajectory_controller` with UR5e **mock hardware** and the upstream `ur_controllers.yaml`: ACCEPTED → SUCCEEDED in 7.6 s, script exits 0 |
| Part 3 in **Gazebo Classic** | ⚠️ **not run**: Gazebo Classic could not be installed (no sudo). The wrapper parses and forwards args (`--show-args` OK). Without Gazebo it fails with `package 'gazebo_ros' not found`, which is the expected "Classic missing" symptom. **Rehearse this on The Construct.** |
| Part 4 Panda demo + `add_collision_box` add/remove | ✅ `eci150_box` appears in `/get_planning_scene` and disappears after `remove:=true`. Plans react as described in §3. |
| RViz GUI clicks (Scene Objects, Joints tab) | ⚠️ not clicked through. The screen was locked during testing, so the UI labels come from the MoveIt Humble plugin. Check whether your build needs the **Publish** button after adding `rviz_box`. |

---

## 5. Troubleshooting

### No display / GPU / GUI windows missing on The Construct
- All windows (turtlesim, RViz, Gazebo, joint sliders, rqt) open in **Graphical Tools** (the web desktop). Open it before launching anything. If it was opened after the launch, close and relaunch.
- If the desktop stream is slow, run `ros2 launch eci150_ur_bringup ur5e_gazebo.launch.py gazebo_gui:=false`. This keeps the physics headless and keeps RViz on the web desktop. Students still see the arm move in RViz.
- RViz black or crashing: try `export LIBGL_ALWAYS_SOFTWARE=1` before launching.

### Gazebo slow, robot "explodes", joints break
- Wait: spawn → `joint_state_broadcaster` → `joint_trajectory_controller` can take 20 to 40 s on a shared ROSject. RViz only starts after JSB is up. Do not send goals before `list_controllers` shows both **active**.
- There is a known historic Gazebo Classic + `gazebo_ros2_control` joint-dynamics issue: the arm collapses or flails at spawn. Use the **current Humble binaries** (the setup script does). If an arm still collapses, note it, restart the launch once, and if that fails switch that student to `gazebo_gui:=false` or pair them with a neighbour. **Do not rebuild plugins in class.**
- Real-time factor well below 1 is normal on The Construct. Trajectories still complete, just more slowly in wall time.

### Controllers not active
- `ros2 control list_controllers` is empty: the `gazebo_ros2_control` plugin did not load. Check the launch log for `libgazebo_ros2_control.so` errors and whether `ros-humble-gazebo-ros2-control` is installed.
- A controller shows `inactive`: the spawner failed or was started with `--stopped`. Run `ros2 control set_controller_state joint_trajectory_controller active` (or `ros2 run controller_manager spawner joint_trajectory_controller -c /controller_manager`).
- `Action server not available`: the action `/joint_trajectory_controller/follow_joint_trajectory` exists only after the JTC spawner finishes. The Python client waits 30 s, then prints a hint.
- A goal is rejected or aborted with `INVALID_JOINTS`: the goal does not name all six joints or misspells one (`allow_partial_joints_goal: false` upstream).

### `use_sim_time`
- Part 3 nodes must use sim time. Gazebo publishes `/clock`, and `robot_state_publisher` uses it. `send_joint_trajectory` turns it on by default and logs `use_sim_time = True`.
- Parts 1 and 4 (mock-hardware Panda demo) use wall time. Do not pass `use_sim_time:=true` there.
- Symptoms of mismatched clocks: action goals hang or time out, TF is "extrapolation into the future/past", and RViz shows the robot frozen. Check with `ros2 param get /<node> use_sim_time` and `ros2 topic hz /clock`.
- Gazebo left running from Part 3 while Part 4 runs means two `/robot_description`s, two controller managers, and a `/clock` publisher. **Stop Gazebo before MoveIt.**

### TF / empty RobotModel in RViz
- `robot_description` is not set: RobotModel shows "No robot description". Check `ros2 topic echo /robot_description --once | head`, or that `robot_state_publisher` is running.
- Wrong Fixed Frame: use `base_link` (or `world`) for the UR5e, and `panda_link0` or `world` for the Panda.
- Links white or missing: `/joint_states` is not published. JSP-GUI is closed in Part 2, or JSB is not active in Part 3.

### Classic vs Fortress mix-ups
- This lab uses **Gazebo Classic 11 only** (`gazebo_ros`, `gazebo_ros2_control`, `ur_simulation_gazebo`). Do not use `ros_gz`, `ign_ros2_control`, `ur_simulation_gz`, or Fortress (`ign gazebo` / `gz sim`).
- If someone installed `ros_gz` next to `gazebo_ros`, the setup script prints a warning. That is harmless as long as nobody launches `ur_simulation_gz`. Typical confusion: running `ur_sim_control.launch.py` from `ur_simulation_gz` (wrong package), or opening `gz sim` by hand.

### Classic missing on the ROSject (fallback)
Which Gazebo a Construct Humble image ships today is **unverified**. If `gzserver` / `gazebo_ros` is missing and cannot be installed (setup script prints `Gazebo Classic (gzserver) not found`):
1. Try `sudo apt-get install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control` (The Construct ROSjects usually allow sudo).
2. If that is impossible, run Part 3 as an **instructor screen-share demo** from a machine or ROSject that has Classic. Students still run the CLI and Python commands as a read-along.
3. Do **not** silently switch students to Fortress / `ur_simulation_gz`. That is a different stack with different launch and controller names. If you choose to do it anyway, write it up as a separate exercise.

### MoveIt planning always fails
- The goal is in collision (red links in RViz) or outside the workspace. Use `<random valid>` or the `ready` goal.
- An old box was left in the scene: run `ros2 run eci150_moveit_demo add_collision_box --ros-args -p remove:=true` and remove `rviz_box` in Scene Objects.
- Increase **Planning Time** to 5 to 10 s in the Planning tab.

### Other
- `Package 'eci150_...' not found`: the workspace is not sourced in that terminal.
- Two nodes with the same name (`WARNING: ... nodes in the graph that share an exact name`): a previous launch is still running. Ctrl+C it, then check `ros2 node list`.

---

## 6. Items still unverified (from the brief)

- Whether The Construct's current Humble image includes Gazebo Classic 11 or only Fortress (see the fallback above).
- Real Gazebo behaviour of Part 3 (spawn time, controller start, arm stability). Rehearse it.
- RViz MotionPlanning Scene Objects flow on the exact plugin build (Publish button present or not).
- The box/sweep recipe was tuned with OMPL defaults (RRTConnect) on `moveit_resources_panda_moveit_config` 2.0.7. Other versions may need small changes to `box_x` / `box_z`.
