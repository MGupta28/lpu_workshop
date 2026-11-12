#!/usr/bin/env bash
# ECI150 Day 4 - workspace setup for a The Construct ROS 2 Humble ROSject.
#
# What it does:
#   1. Checks we are on ROS 2 Humble.
#   2. Installs the apt packages the lab needs (Gazebo Classic 11 stack,
#      ur_description, MoveIt + Panda demo, turtlesim, tf2_tools, ...).
#   3. Creates ~/eci150_ws/src, links this repo into it and clones
#      ur_simulation_gazebo (humble branch, source only - not on apt).
#   4. Runs rosdep and colcon build.
#
# Usage:   bash scripts/setup_workspace.sh
# Options (environment variables):
#   ECI150_WS=~/eci150_ws     workspace location
#   SKIP_APT=1                do not call apt-get / rosdep (no sudo)
#
# Stack rule for this lab: Gazebo CLASSIC 11 (gazebo_ros + gazebo_ros2_control).
# Do NOT install ros_gz / ur_simulation_gz / Gazebo Fortress for this lab.

set -eo pipefail

WS="${ECI150_WS:-$HOME/eci150_ws}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_NAME="$(basename "$REPO_DIR")"

say()  { echo -e "\033[1;32m[eci150]\033[0m $*"; }
warn() { echo -e "\033[1;33m[eci150 WARNING]\033[0m $*"; }
die()  { echo -e "\033[1;31m[eci150 ERROR]\033[0m $*"; exit 1; }

# ---------------------------------------------------------------- 1. ROS 2
[ -f /opt/ros/humble/setup.bash ] || die "/opt/ros/humble not found. Use a ROS 2 Humble ROSject."
# ROS setup scripts reference unset variables, so source them without `set -u`.
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash
say "ROS_DISTRO=$ROS_DISTRO, workspace: $WS"

# ---------------------------------------------------------------- 2. apt packages
APT_PKGS=(
  # Part 1
  ros-humble-turtlesim
  # Part 2
  ros-humble-ur-description
  ros-humble-joint-state-publisher-gui
  ros-humble-robot-state-publisher
  ros-humble-xacro
  ros-humble-rviz2
  ros-humble-tf2-tools
  ros-humble-rqt-tf-tree
  ros-humble-launch-xml
  # Part 3 (Gazebo Classic 11 + ros2_control)
  ros-humble-gazebo-ros-pkgs
  ros-humble-gazebo-ros2-control
  ros-humble-ros2-control
  ros-humble-ros2-controllers
  ros-humble-controller-manager
  ros-humble-joint-state-broadcaster
  ros-humble-joint-trajectory-controller
  ros-humble-ur-controllers
  ros-humble-ur-moveit-config
  # Part 4 (MoveIt 2 Panda demo)
  ros-humble-moveit
  ros-humble-moveit-resources-panda-moveit-config
  ros-humble-moveit-resources-panda-description
  # tools
  python3-colcon-common-extensions
  python3-rosdep
  python3-vcstool
  git
)

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if sudo -n true 2>/dev/null; then SUDO="sudo"; else SKIP_APT=1; warn "No passwordless sudo: skipping apt/rosdep."; fi
fi

if [ -z "${SKIP_APT:-}" ]; then
  say "Installing apt packages (this can take a few minutes) ..."
  $SUDO apt-get update -qq
  # Install one by one so a single missing package does not stop the rest.
  MISSING=()
  for p in "${APT_PKGS[@]}"; do
    if ! dpkg -s "$p" >/dev/null 2>&1; then
      DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq "$p" >/dev/null 2>&1 || MISSING+=("$p")
    fi
  done
  [ ${#MISSING[@]} -eq 0 ] || warn "Could not install: ${MISSING[*]} (see INSTRUCTOR_NOTES.md)"
fi

# ---------------------------------------------------------------- 3. workspace + sources
mkdir -p "$WS/src"
cd "$WS/src"

# Put this repo inside the workspace (symlink if it was cloned elsewhere).
if [ "$(cd "$REPO_DIR/.." && pwd)" != "$(pwd)" ] && [ ! -e "$REPO_NAME" ]; then
  ln -s "$REPO_DIR" "$REPO_NAME"
  say "Linked $REPO_DIR -> $WS/src/$REPO_NAME"
fi

# ur_simulation_gazebo (Classic) is not released on apt for Humble -> source.
if [ ! -d Universal_Robots_ROS2_Gazebo_Simulation ]; then
  say "Cloning Universal_Robots_ROS2_Gazebo_Simulation (humble) ..."
  git clone -q -b humble --depth 1 \
    https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation.git
fi

# ur_description is normally on apt; fall back to source if it is not.
if ! ros2 pkg prefix ur_description >/dev/null 2>&1 && [ ! -d Universal_Robots_ROS2_Description ]; then
  warn "ur_description binary not found - cloning it from source (humble)."
  git clone -q -b humble --depth 1 \
    https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git
fi

# ---------------------------------------------------------------- 4. rosdep + build
if [ -z "${SKIP_APT:-}" ]; then
  [ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || $SUDO rosdep init || true
  rosdep update -q || warn "rosdep update failed (offline?)"
  rosdep install --from-paths . --ignore-src -r -y --rosdistro humble \
    || warn "rosdep could not resolve every key (see output above)."
fi

cd "$WS"
say "Building with colcon ..."
colcon build

# ---------------------------------------------------------------- 5. sanity checks
# shellcheck disable=SC1091
source "$WS/install/setup.bash"
say "Checking the lab stack:"
for p in turtlesim ur_description ur_simulation_gazebo gazebo_ros gazebo_ros2_control \
         joint_trajectory_controller moveit_resources_panda_moveit_config \
         eci150_turtle_demo eci150_ur_bringup eci150_ur_control eci150_moveit_demo; do
  if ros2 pkg prefix "$p" >/dev/null 2>&1; then echo "   OK       $p"; else echo "   MISSING  $p"; fi
done

if command -v gzserver >/dev/null 2>&1; then
  echo "   OK       Gazebo Classic: $(gzserver --version 2>/dev/null | grep -m1 -o 'version [0-9.]*' || echo found)"
else
  warn "Gazebo Classic (gzserver) not found. Part 3 will not run - see INSTRUCTOR_NOTES.md 'Classic missing'."
fi
if ros2 pkg prefix ros_gz_sim >/dev/null 2>&1 || ros2 pkg prefix ur_simulation_gz >/dev/null 2>&1; then
  warn "ros_gz / ur_simulation_gz is also installed. Do not use them in this lab (Classic only)."
fi

cat <<EOF

[eci150] Done. In EVERY new terminal run:

    source $WS/install/setup.bash

Then follow STUDENT_GUIDE.md.
EOF
