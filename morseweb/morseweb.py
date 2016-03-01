from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from pymorse.stream import StreamJSON, PollThread
from pymorse import Morse

from json.decoder import JSONDecodeError
from os.path import basename, splitext

import autoexport


class AppSession(ApplicationSession):
    log = Logger()

    def onConnect(self):
        self.join(self.config.realm)

        self.node_stream = StreamJSON("localhost", 65000)
        self.poll_thread = PollThread()
        self.simu = Morse()

        self.poll_thread.start()
        self.export_models()

    def onDisconnect(self):
        self.poll_thread.syncstop()
        self.node_stream.close()
        self.simu.close()

    @inlineCallbacks
    def onJoin(self, details):
        self.publish_stream()

        reg = yield self.register(self.get_scene, "com.simulation.get_scene")

    @inlineCallbacks
    def publish_stream(self):
        while self.node_stream.is_up():
            self.node_stream.publish(["morseweb", {}])

            try:
                data = (self.node_stream.get(timeout=1e-3) or
                        self.node_stream.last())
            except JSONDecodeError:
                pass
            else:
                self.publish("com.simulation.update", data)

            yield sleep(1e-1)

    def get_robots(self):
        self.node_stream.publish(["morseweb", {}])

        robots = self.simu.rpc("simulation", "details")["robots"]
        data = (self.node_stream.get(timeout=1e-3) or
                self.node_stream.last())

        foo = [{"name": robot["name"],
                 "model": robot["type"].lower(),
                 "position": data[robot["name"]][0],
                 "rotation": data[robot["name"]][1],
                 "type": "robot"}
                for robot in robots]

        return foo

    def get_passive_objects(self):
        objects = self.simu.rpc("simulation", "get_scene_objects")

        return [{"name": k.rsplit("_", 1)[0],
                 "model": k.split("_", 1)[0],
                 "position": v[1],
                 "rotation": v[2],
                 "type": "passive"}
                for k, v in objects.items() if k.endswith("_passive")]

    def get_scene(self):
        cx, cy, cz = self.simu.rpc("simulation", "get_camarafp_position")
        environment = self.simu.rpc("simulation", "details")["environment"]
        environment = basename(splitext(environment)[0])

        return {"camera_position": {"x": cx, "y": cy, "z": cz},
                "environment": environment,
                "items": self.get_robots() + self.get_passive_objects()}

    def export_models(self):
        scene = self.get_scene()
        items = [item["model"] for item in scene["items"]]

        autoexport.init()
        autoexport.export(items + [scene["environment"]])
