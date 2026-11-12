"""Part 1: make turtle1 drive in a circle.

ROS 2 vocabulary used here:
  * A *node* is one running program that takes part in the ROS graph.
  * A *topic* is a named channel. Publishers write messages to it and
    subscribers read them. Nobody needs to know who is on the other end.
  * A *parameter* is a named setting stored inside a node that you can change
    from the command line without editing the code.

This node publishes a geometry_msgs/msg/Twist (a velocity command) on
/turtle1/cmd_vel twice per second. A constant forward speed plus a constant
turning speed makes the turtle drive a circle.

Try it:
  ros2 run eci150_turtle_demo circle_publisher
  ros2 run eci150_turtle_demo circle_publisher --ros-args -p linear_x:=2.0 -p angular_z:=0.5
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CirclePublisher(Node):
    """A node that publishes the same velocity command again and again."""

    def __init__(self):
        # Every node has a name. This is what `ros2 node list` will show.
        super().__init__('circle_publisher')

        # Declare parameters with default values. Students can override them
        # with `--ros-args -p linear_x:=...` or `ros2 param set` at runtime.
        self.declare_parameter('linear_x', 1.0)   # forward speed  [m/s]
        self.declare_parameter('angular_z', 1.0)  # turning speed  [rad/s]

        # Create a publisher: message type, topic name, queue depth.
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # A timer calls self.publish_velocity every 0.5 s, i.e. at 2 Hz.
        self.timer = self.create_timer(0.5, self.publish_velocity)

        self.get_logger().info(
            'circle_publisher started: publishing Twist on /turtle1/cmd_vel at 2 Hz '
            f'(linear_x={self.get_parameter("linear_x").value}, '
            f'angular_z={self.get_parameter("angular_z").value})'
        )

    def publish_velocity(self):
        """Build one Twist message and send it."""
        msg = Twist()  # every field starts at 0.0
        # Read the parameters each time, so `ros2 param set` takes effect live.
        msg.linear.x = float(self.get_parameter('linear_x').value)
        msg.angular.z = float(self.get_parameter('angular_z').value)
        # linear.y, linear.z, angular.x, angular.y stay 0: a turtle is 2-D.
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)          # start the ROS 2 client library
    node = CirclePublisher()
    try:
        rclpy.spin(node)           # keep the node alive so the timer fires
    except KeyboardInterrupt:
        pass                       # Ctrl+C is the normal way to stop
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
