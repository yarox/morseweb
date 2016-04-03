#! /usr/bin/env morseexec

from morse.builder import *


# Create a robot
robot = ATRV()
robot.translate(1, 1, 0)

motion = MotionVW()
robot.append(motion)

robot.add_default_interface("socket")

# Load some passive objects
# NOTE: you should set the name of the object exactly as the name of the model
# you're loading.
obj0 = PassiveObject("props/objects", "SmallTable")
obj0.name = "SmallTable"
obj0.translate(2, 2, 0)
obj0.rotate(z=0)

obj1 = PassiveObject("props/objects", "SmallTable")
obj1.name = "SmallTable"
obj1.translate(-2, -2, 0)
obj1.rotate(z=0.7)

# Configure the environment
env = Environment("empty", fastmode=True)
env.set_camera_location([0, 10, 15])

# morseweb needs "use_relative_time" and "configure_multinode" to work
env.use_relative_time(True)
env.configure_multinode(
    protocol = "socket",
    server_address = "localhost",
    server_port = "65000",
    distribution = {"nodeA": [robot.name]}
)

env.create()
