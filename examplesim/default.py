#! /usr/bin/env morseexec

from examplesim.builder.sensors import ExtraServices
from morse.builder import *


# Create a robot
robot = ATRV()
robot.translate(0, 0, 0)

motion = MotionVW()
robot.append(motion)

robot.add_default_interface("socket")

# Load some passive objects
# Passive object name convention: "<model>_<id>_passive"
# + <id> defined in case there are multiple copies of the same object
# + <model>.json should exist in the models directory
table0 = PassiveObject("props/objects", "SmallTable")
table0.translate(1, 1, 0)
table0.rotate(z=0.2)
table0.name = "table_0_passive"

table1 = PassiveObject("props/objects", "SmallTable")
table1.translate(2, 2, 0)
table1.rotate(z=0.7)
table1.name = "table_1_passive"

# Create a fake robot holding the simulator extra services for morseweb
fakerobot = FakeRobot()
extra = ExtraServices()
fakerobot.append(extra)
fakerobot.add_default_interface("socket")

# Configure the environment
env = Environment("empty", fastmode=True)
env.set_camera_location([0, 10, 15])

env.configure_multinode(
    protocol = "socket",
    server_address = "localhost",
    server_port = "65000",
    distribution = {"nodeA": [robot.name, fakerobot.name]}
)

env.create()
