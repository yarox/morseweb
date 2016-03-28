from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.util import sleep

from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from pymorse.stream import StreamJSON, PollThread
from pymorse import Morse

from json.decoder import JSONDecodeError
from os.path import basename, splitext

from autoexport import BlenderModel

import autoexport


class AppSession(ApplicationSession):
    log = Logger()

    def onConnect(self):
        self.join(self.config.realm)

        self.node_stream = StreamJSON("localhost", 65000)
        self.poll_thread = PollThread()
        self.simu = Morse()

        self.poll_thread.start()
        self.start()
        self.export_models()

    def onDisconnect(self):
        self.poll_thread.syncstop()
        self.node_stream.close()
        self.simu.close()

    def start(self):
        self.objects = self.simu.rpc("simulation", "get_scene_objects")
        self.details = self.simu.rpc("simulation", "details")
        self.robots = self.simu.rpc("simulation", "list_robots")

        self.node_stream.publish(["morseweb", {}])
        self.node_data = (self.node_stream.get(timeout=1e-3) or
                          self.node_stream.last())

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
        robots = self.details["robots"]

        return [{"name": robot["name"],
                 "model": robot["type"].lower(),
                 "position": self.node_data[robot["name"]][0],
                 "rotation": self.node_data[robot["name"]][1],
                 "type": "robot"}
                for robot in robots]

    def get_passive_objects(self):
        return [{"name": k,
                 "model": k.split(".")[0].lower(),
                 "position": v[1],
                 "rotation": v[2],
                 "type": "passive"}
                for k, v in self.objects.items()
                if k.split(".")[0].lower() in self.passive_object_names]

    def get_scene(self):
        cx, cy, cz = self.simu.rpc("simulation", "get_camarafp_position")
        environment = basename(splitext(self.details["environment"])[0])

        return {"camera_position": {"x": cx, "y": cy, "z": cz},
                "environment": environment,
                "items": self.get_robots() + self.get_passive_objects()}

    def export_models(self):
        self.log.info("Exporting models. This operation may take a while.")
        autoexport.init()

        # We have to export three different set of objects from the simulation:
        # the scene, the robots, and the passive objects. We can get the scene
        # and the robots easily from the simulation. But passive objects are
        # a little more complicated to obtain. Here's how we do it:
        # 1. Get all objects in the simulation
        # 2. Remove the robots
        # 3. Remove the objects from the environment file
        # The remaining objects should be passive objects only.

        environment_name = basename(splitext(self.details["environment"])[0])
        environment = BlenderModel.get(name=environment_name)

        environment_objects = BlenderModel.select().where(
                                (BlenderModel.path == environment.path) &
                                (BlenderModel.name != environment.name))

        environment_objects = [object.name for object in environment_objects]
        all_objects = [name.split(".")[0].lower() for name in self.objects.keys()]
        robots = [robot["type"].lower() for robot in self.details["robots"]]

        # FIXME: This will remove a legitimate passive object if it shares
        # the same name with an object in the environment file. Until fixed,
        # make sure your passive object's names are unique.
        objects = set(all_objects) - set(environment_objects) - set(self.robots)
        model_names = robots + list(objects)

        models = BlenderModel.select().where(BlenderModel.name << model_names)
        self.passive_object_names = [model.name for model in models]

        autoexport.export(self.passive_object_names + [environment.name])

        self.log.info("Done exporting models.")
