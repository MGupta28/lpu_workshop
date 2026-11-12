"""Part 1: listen to where turtle1 is.

turtlesim publishes the turtle's pose (position + heading) on /turtle1/pose
about 60 times per second. This node *subscribes* to that topic: every time a
message arrives, ROS calls our callback function with it.

Printing 60 lines per second would flood the terminal, so we throttle the log
to about once per second.

Try it:
  ros2 run eci150_turtle_demo pose_subscriber
"""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class PoseSubscriber(Node):
    """A node that prints the turtle pose roughly once per second."""

    def __init__(self):
        super().__init__('pose_subscriber')

        # Create a subscription: message type, topic name, callback, queue depth.
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)

        self.get_logger().info('pose_subscriber started: listening on /turtle1/pose')

    def on_pose(self, msg: Pose):
        """Run automatically each time a new Pose message arrives."""
        # throttle_duration_sec=1.0 means: print at most once per second,
        # even though this callback runs ~60 times per second.
        self.get_logger().info(
            f'x={msg.x:5.2f}  y={msg.y:5.2f}  theta={msg.theta:+5.2f} rad  '
            f'v={msg.linear_velocity:4.2f} m/s  w={msg.angular_velocity:+4.2f} rad/s',
            throttle_duration_sec=1.0,
        )


def main(args=None):
    rclpy.init(args=args)
    node = PoseSubscriber()
    try:
        rclpy.spin(node)  # wait for messages and call on_pose for each one
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
