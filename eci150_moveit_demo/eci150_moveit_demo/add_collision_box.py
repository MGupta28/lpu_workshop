"""Part 4: put a box in front of the Panda so MoveIt has to plan around it.

ROS 2 / MoveIt vocabulary used here:
  * The *planning scene* is MoveIt's picture of the world: the robot plus any
    obstacles ("collision objects"). The planner will not plan through them.
  * A *service* is a request/response call (like a function call over the
    network). move_group offers /apply_planning_scene: we send a small change
    to the scene (a "diff"), it applies it and answers success true/false.

This node adds (or removes) ONE box called `eci150_box`, then exits.

Run it (with the Panda demo.launch.py already running):
  ros2 run eci150_moveit_demo add_collision_box
  ros2 run eci150_moveit_demo add_collision_box --ros-args -p remove:=true
  ros2 run eci150_moveit_demo add_collision_box --ros-args -p box_x:=0.5 -p box_z:=0.3
"""

import sys

import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive

SERVICE_NAME = '/apply_planning_scene'
BOX_ID = 'eci150_box'
FRAME_ID = 'panda_link0'           # the Panda's base frame
BOX_SIZE = [0.15, 0.15, 0.40]      # x, y, z size in metres


class AddCollisionBox(Node):
    """Add or remove the course collision box via a planning-scene diff."""

    def __init__(self):
        super().__init__('add_collision_box')
        # Parameters so students can reset the scene or move the box without editing code.
        self.declare_parameter('remove', False)
        self.declare_parameter('box_x', 0.40)  # in front of the robot
        self.declare_parameter('box_y', 0.00)
        self.declare_parameter('box_z', 0.20)  # box centre; 0.40 m tall -> sits on z = 0
        self.client = self.create_client(ApplyPlanningScene, SERVICE_NAME)

    def build_collision_object(self, remove):
        obj = CollisionObject()
        obj.id = BOX_ID
        obj.header.frame_id = FRAME_ID
        if remove:
            # To remove, MoveIt only needs the id and the REMOVE operation.
            obj.operation = CollisionObject.REMOVE
            return obj

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = BOX_SIZE

        pose = Pose()
        pose.position.x = float(self.get_parameter('box_x').value)
        pose.position.y = float(self.get_parameter('box_y').value)
        pose.position.z = float(self.get_parameter('box_z').value)
        pose.orientation.w = 1.0  # identity orientation (no rotation)

        obj.primitives = [box]
        obj.primitive_poses = [pose]
        obj.operation = CollisionObject.ADD
        return obj

    def run(self):
        log = self.get_logger()
        remove = bool(self.get_parameter('remove').value)

        # 1. Wait until move_group offers the service.
        log.info(f'Waiting for service {SERVICE_NAME} (is demo.launch.py running?) ...')
        if not self.client.wait_for_service(timeout_sec=30.0):
            log.error(f'{SERVICE_NAME} not available. Start the Panda demo first.')
            return False

        # 2. Wrap our object in a PlanningScene *diff*: "change only this, keep the rest".
        scene = PlanningScene()
        scene.is_diff = True
        scene.world.collision_objects = [self.build_collision_object(remove)]

        # 3. Call the service and wait for the answer.
        future = self.client.call_async(ApplyPlanningScene.Request(scene=scene))
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        if response is None or not response.success:
            log.error('move_group did not accept the planning-scene change.')
            return False

        if remove:
            log.info(f'Removed "{BOX_ID}" from the planning scene. Re-plan in RViz.')
        else:
            p = self.build_collision_object(False).primitive_poses[0].position
            log.info(f'Added "{BOX_ID}" ({BOX_SIZE[0]} x {BOX_SIZE[1]} x {BOX_SIZE[2]} m) at '
                     f'x={p.x:.2f} y={p.y:.2f} z={p.z:.2f} in {FRAME_ID}. '
                     'Now press Plan again in RViz and compare the path.')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = AddCollisionBox()
    ok = False
    try:
        ok = node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
