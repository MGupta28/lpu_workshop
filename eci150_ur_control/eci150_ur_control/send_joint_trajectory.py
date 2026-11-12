"""Part 3: move the simulated UR5e with a FollowJointTrajectory *action*.

ROS 2 vocabulary used here:
  * An *action* is for jobs that take time (like moving an arm for a few
    seconds). The client sends a *goal*, the server (here, the
    joint_trajectory_controller) says "accepted" or "rejected", may send
    *feedback* while it works, and finally sends a *result*.
  * A *joint trajectory* is a list of *points*. Each point says "these six
    joint angles (radians) should be reached this many seconds after start".

This script sends ONE goal with two points, waits for the result, prints it,
and exits:
  1. HOME_POSE      - the upright pose the robot spawns in (safe start).
  2. TEACHING_POSE  - a gentle shoulder-pan + elbow bend, well inside limits.

Run it (with ur5e_gazebo.launch.py already running):
  ros2 run eci150_ur_control send_joint_trajectory
  ros2 run eci150_ur_control send_joint_trajectory --ros-args -p home_only:=true

Sim time: Gazebo publishes its own clock on /clock. Every node that talks to
the simulation should use it, so this script turns use_sim_time ON by default
(you can still pass `-p use_sim_time:=false` yourself).
"""

import sys

import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter
from trajectory_msgs.msg import JointTrajectoryPoint

ACTION_NAME = '/joint_trajectory_controller/follow_joint_trajectory'

# The controller expects all six UR joints, in this order.
JOINT_NAMES = [
    'shoulder_pan_joint',
    'shoulder_lift_joint',
    'elbow_joint',
    'wrist_1_joint',
    'wrist_2_joint',
    'wrist_3_joint',
]

# Joint angles in radians, same order as JOINT_NAMES.
# HOME_POSE matches ur_description/config/initial_positions.yaml (arm upright).
HOME_POSE = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
# A clearly different, reachable pose: pan ~34 deg, lean forward, bend elbow ~52 deg.
TEACHING_POSE = [0.6, -1.2, 0.9, -1.3, -1.57, 0.0]

HOME_TIME_S = 3       # reach HOME_POSE 3 s after the goal starts
TEACHING_TIME_S = 7   # reach TEACHING_POSE 7 s after the goal starts

# Human-readable names for FollowJointTrajectory.Result.error_code values.
ERROR_CODES = {
    FollowJointTrajectory.Result.SUCCESSFUL: 'SUCCESSFUL',
    FollowJointTrajectory.Result.INVALID_GOAL: 'INVALID_GOAL',
    FollowJointTrajectory.Result.INVALID_JOINTS: 'INVALID_JOINTS',
    FollowJointTrajectory.Result.OLD_HEADER_TIMESTAMP: 'OLD_HEADER_TIMESTAMP',
    FollowJointTrajectory.Result.PATH_TOLERANCE_VIOLATED: 'PATH_TOLERANCE_VIOLATED',
    FollowJointTrajectory.Result.GOAL_TOLERANCE_VIOLATED: 'GOAL_TOLERANCE_VIOLATED',
}


def make_point(positions, seconds):
    """Build one trajectory point that should be reached `seconds` after start."""
    point = JointTrajectoryPoint()
    point.positions = [float(p) for p in positions]
    point.velocities = [0.0] * len(positions)  # come to rest at each point
    point.time_from_start = Duration(sec=seconds, nanosec=0)
    return point


class SendJointTrajectory(Node):
    """A tiny action client: send one goal, wait, report, done."""

    def __init__(self, parameter_overrides=None):
        super().__init__('send_joint_trajectory', parameter_overrides=parameter_overrides)
        self.declare_parameter('home_only', False)  # true = just go back to HOME_POSE
        self.client = ActionClient(self, FollowJointTrajectory, ACTION_NAME)

    def build_goal(self):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINT_NAMES
        # header.stamp is left at zero, which means "start as soon as you get it".
        if self.get_parameter('home_only').value:
            goal.trajectory.points = [make_point(HOME_POSE, HOME_TIME_S)]
        else:
            goal.trajectory.points = [
                make_point(HOME_POSE, HOME_TIME_S),
                make_point(TEACHING_POSE, TEACHING_TIME_S),
            ]
        return goal

    def run(self):
        """Send the goal and block until the result arrives. Returns True on success."""
        log = self.get_logger()
        log.info(f'use_sim_time = {self.get_parameter("use_sim_time").value}')

        # 1. Wait until the controller's action server exists.
        log.info(f'Waiting for action server {ACTION_NAME} ...')
        if not self.client.wait_for_server(timeout_sec=30.0):
            log.error('Action server not available. Is ur5e_gazebo.launch.py running and '
                      'is joint_trajectory_controller active? (ros2 control list_controllers)')
            return False

        # 2. Send the goal and wait for "accepted" / "rejected".
        goal = self.build_goal()
        for p in goal.trajectory.points:
            log.info(f'  t={p.time_from_start.sec} s -> {list(p.positions)}')
        send_future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            log.error('Goal REJECTED by the controller.')
            return False
        log.info('Goal ACCEPTED - watch the arm move in Gazebo and RViz.')

        # 3. Wait for the final result.
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result
        code = ERROR_CODES.get(result.error_code, str(result.error_code))
        if result.error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            log.info('Goal SUCCEEDED.')
            return True
        log.error(f'Goal ABORTED/FAILED: error_code={code}, error_string="{result.error_string}"')
        return False


def main(args=None):
    rclpy.init(args=args)

    # Default to simulation time unless the user set use_sim_time themselves.
    cli = ' '.join(sys.argv if args is None else args)
    overrides = None if 'use_sim_time' in cli else [Parameter('use_sim_time', value=True)]

    node = SendJointTrajectory(parameter_overrides=overrides)
    ok = False
    try:
        ok = node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(0 if ok else 1)  # exit after the result; do not spin forever


if __name__ == '__main__':
    main()
