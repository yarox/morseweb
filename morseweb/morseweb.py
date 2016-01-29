from autobahn.twisted.wamp import ApplicationSession

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from functools import partial
from pymorse import Morse


class AppSession(ApplicationSession):

    simu = Morse()
    log = Logger()

    @inlineCallbacks
    def callback_pose(self, data, name):
        yield self.publish("com.{}.pose".format(name), data, name=name)

    @inlineCallbacks
    def callback_time(self, data):
        yield self.publish("com.simulation.time", data)

    @inlineCallbacks
    def onJoin(self, details):
        for name in self.simu.robots:
            if name != "fakerobot":
                self.log.info("subscribed to {name}", name=name)

                callback = partial(self.callback_pose, name=name)
                getattr(self.simu, name).pose.subscribe(callback)

        self.simu.fakerobot.extra.subscribe(self.callback_time)

        def get_robots():
            robots = self.simu.rpc("simulation", "details")["robots"]

            return [{"name": robot["name"],
                     "model": robot["type"].lower()}
                    for robot in robots if robot["type"].lower() != "fakerobot"]

        def get_start_time():
            return self.simu.rpc("fakerobot.extra", "get_start_time")

        def get_scene():
            cx, cy, cz = self.simu.rpc("fakerobot.extra", "get_camera_position")
            environment = self.simu.rpc("fakerobot.extra", "get_environment")
            robots = get_robots()

            return {"camera_position": {"x": cx, "y": cy, "z": cz},
                    "environment": environment,
                    "robots": robots}

        reg1 = yield self.register(get_start_time, "com.simulation.get_start_time")
        reg2 = yield self.register(get_scene, "com.simulation.get_scene")
