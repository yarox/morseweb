from os.path import basename, splitext

from autoexport import BlenderModel
from flask_socketio import SocketIO
from pymorse import Morse

import autoexport
import ujson
import redis
import sys


TOPIC_STATUS = "simulator.status"
TOPIC_READY = "simulator.ready"


def setup_models(simu, socketio, queue):
    socketio.emit(TOPIC_STATUS, {"data": "Connecting with the simulation"})

    camera_position = simu.rpc("simulation", "get_camarafp_position")
    robot_names = simu.rpc("simulation", "list_robots")
    objects = simu.rpc("simulation", "get_scene_objects")
    details = simu.rpc("simulation", "details")

    socketio.emit(TOPIC_STATUS, {"data": "Loading models into the database"})
    autoexport.init()

    environment_name = basename(splitext(details["environment"])[0])
    environment = BlenderModel.get(name=environment_name)

    environment_models = BlenderModel.get_models_from_environment(environment)
    environment_models = [model.name for model in environment_models]

    all_models = [name.split(".")[0].lower() for name in objects.keys()]
    robots = [robot["type"].lower() for robot in details["robots"]]

    models = set(all_models) - set(environment_models) - set(robot_names)
    model_names = robots + list(models)

    models = BlenderModel.get_models_from_names(model_names)
    passive_object_names = [model.name for model in models]

    socketio.emit(TOPIC_STATUS, {"data": "Exporting models from the simulation"})
    autoexport.export(passive_object_names + [environment.name])

    socketio.emit(TOPIC_STATUS, {"data": "Synchronizing data with the app"})
    info_passive_objects = [{"name": k,
                             "model": k.split(".")[0].lower(),
                             "position": v[1],
                             "rotation": v[2],
                             "type": "passive"}
                            for k, v in objects.items()
                            if k.split(".")[0].lower() in passive_object_names]

    info_robots = [{"name": robot["name"],
                     "model": robot["type"].lower(),
                     "position": [0, 0, 0],
                     "rotation": [0, 0, 0, 0],
                     "type": "robot"}
                    for robot in details["robots"]]

    environment = basename(splitext(details["environment"])[0])
    cx, cy, cz = camera_position

    scene = {"camera_position": {"x": cx, "y": cy, "z": cz},
             "environment": environment,
             "items": info_robots + info_passive_objects}

    queue.set("scene", ujson.dumps(scene))
    socketio.emit(TOPIC_READY, {})


if __name__ == "__main__":
    message_queue = sys.argv[1]

    socketio = SocketIO(message_queue=message_queue)
    queue = redis.StrictRedis()
    simu = Morse()

    setup_models(simu, socketio, queue)
