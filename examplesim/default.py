#! /usr/bin/env morseexec

from examplesim.builder.sensors import ExtraServices
from morse.builder import *


robot = ATRV()
robot.translate(0, 0, 0)

motion = MotionVW()
robot.append(motion)

robot.add_default_interface("socket")

# Fake robot holding the simulator extra services for morseweb
fakerobot = FakeRobot()
extra = ExtraServices()
fakerobot.append(extra)
fakerobot.add_default_interface("socket")

# Environment configuration
env = Environment("empty", fastmode=True)
env.set_camera_location([0, 10, 15])

env.configure_multinode(
    protocol = "socket",
    server_address = "localhost",
    server_port = "65000",
    distribution = {"nodeA": [robot.name, fakerobot.name]}
)

env.create()
