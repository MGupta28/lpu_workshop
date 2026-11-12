# ECI150 Day 4: ROS 2 practical (Orangewood)

A 2-hour online ROS 2 Humble lab that runs on **The Construct**. Course designer: Manan Gupta.

- **Students:** follow [`STUDENT_GUIDE.md`](STUDENT_GUIDE.md).
- **Instructors:** read [`INSTRUCTOR_NOTES.md`](INSTRUCTOR_NOTES.md) (setup, timing, answers, troubleshooting).

## Quick setup (instructor, once per ROSject)

```bash
mkdir -p ~/eci150_ws/src && cd ~/eci150_ws/src
git clone <COURSE_REPO_URL> eci150_day4_lab
bash eci150_day4_lab/scripts/setup_workspace.sh
source ~/eci150_ws/install/setup.bash
```

## Packages

| Package | Part | Contents |
| --- | --- | --- |
| `eci150_turtle_demo` | 1 | `circle_publisher`, `pose_subscriber`, `turtle_demo.launch.py` |
| `eci150_ur_bringup` | 2, 3 | `view_ur5e.launch.py`, `view_panda.launch.py`, `ur5e_gazebo.launch.py` (wrappers around upstream `ur_description` / `ur_simulation_gazebo`) |
| `eci150_ur_control` | 3 | `send_joint_trajectory` (FollowJointTrajectory action client) |
| `eci150_moveit_demo` | 4 | `add_collision_box` (adds/removes `eci150_box` via `/apply_planning_scene`) |

Stack: ROS 2 Humble, Ubuntu 22.04, Gazebo Classic 11 (`gazebo_ros`, `gazebo_ros2_control`), UR5e (`ur_description`, `ur_simulation_gazebo` humble), and the MoveIt 2 Panda demo (`moveit_resources_panda_moveit_config`).
