from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from pymorse.stream import StreamJSON, PollThread
from pymorse import Morse

from json.decoder import JSONDecodeError
from functools import partial


class AppSession(ApplicationSession):
    poll_thread = PollThread()
    streams = []

    simu = Morse()
    log = Logger()

    def onDisconnect(self):
        for stream in self.streams:
            stream.close()

        self.poll_thread.syncstop()

    @inlineCallbacks
    def onJoin(self, details):
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

        self.publish_stream()

        reg1 = yield self.register(get_start_time, "com.simulation.get_start_time")
        reg2 = yield self.register(get_scene, "com.simulation.get_scene")

    @inlineCallbacks
    def publish_stream(self):
        pose_stream_port = 65000
        time_stream_port = self.simu.rpc("simulation", "get_stream_port",
                                         "fakerobot.extra")

        pose_stream = StreamJSON("localhost", pose_stream_port)
        time_stream = StreamJSON("localhost", time_stream_port)

        self.streams = ([pose_stream, time_stream])
        self.poll_thread.start()

        while all(stream.is_up() for stream in self.streams):
            # Get pose information
            pose_stream.publish(["morseweb", {}])

            try:
                pose_data = (pose_stream.get(timeout=1e-3) or
                             pose_stream.last())
            except JSONDecodeError as e:
                self.log.warn("pose_data {exception}", exception=e)
                pose_data = {}

            try:
                del pose_data["fakerobot"]
            except KeyError:
                pass

            # Get time information
            try:
                time_data = (time_stream.get(timeout=1e-3) or
                             time_stream.last())
            except JSONDecodeError as e:
                self.log.warn("time_data {exception}", exception=e)
                time_data = {}

            # Publish data to each topic
            self.publish("com.simulation.time", time_data)
            self.publish("com.robots.pose", pose_data)

            yield sleep(1e-2)
