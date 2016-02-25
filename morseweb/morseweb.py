from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from pymorse.stream import StreamJSON, PollThread
from pymorse import Morse

from json.decoder import JSONDecodeError
from os.path import basename, splitext


class AppSession(ApplicationSession):
    node_stream = StreamJSON("localhost", 65000)
    poll_thread = PollThread()

    simu = Morse()
    log = Logger()

    def onDisconnect(self):
        self.poll_thread.syncstop()
        self.node_stream.close()

    @inlineCallbacks
    def onJoin(self, details):
        self.publish_stream()

        def get_robots():
            robots = self.simu.rpc("simulation", "details")["robots"]
            data = (self.node_stream.get(timeout=1e-3) or
                    self.node_stream.last())

            return [{"name": robot["name"],
                     "model": robot["type"].lower(),
                     "position": data[robot["name"]][0],
                     "rotation": data[robot["name"]][1],
                     "type": "robot"}
                    for robot in robots]

        def get_passive_objects():
            objects = self.simu.rpc("simulation", "get_scene_objects")

            return [{"name": k.rsplit("_", 1)[0],
                     "model": k.split("_", 1)[0],
                     "position": v[1],
                     "rotation": v[2],
                     "type": "passive"}
                    for k, v in objects.items() if k.endswith("_passive")]

        def get_scene():
            cx, cy, cz = self.simu.rpc("simulation", "get_camarafp_position")
            environment = self.simu.rpc("simulation", "details")["environment"]
            environment = basename(splitext(environment)[0])

            return {"camera_position": {"x": cx, "y": cy, "z": cz},
                    "environment": environment,
                    "items": get_robots() + get_passive_objects()}

        reg = yield self.register(get_scene, "com.simulation.get_scene")

    @inlineCallbacks
    def publish_stream(self):
        time_data = {"simtime": 0, "realtime": 0}
        self.poll_thread.start()

        while self.node_stream.is_up():
            self.node_stream.publish(["morseweb", {}])

            try:
                data = (self.node_stream.get(timeout=1e-3) or
                        self.node_stream.last() or {})
            except JSONDecodeError:
                pass
            else:
                (time_data["simtime"], _,
                 time_data["realtime"]) = data.pop("__time", [0, 0, 0])

                self.publish("com.simulation.time", time_data)
                self.publish("com.robots.pose", data)

            yield sleep(1e-2)
