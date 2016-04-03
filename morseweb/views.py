from flask import render_template, jsonify, url_for
from threading import Thread

from morseweb import app

import subprocess
import ujson
import redis
import os


SCENE_READY = False
THREAD = None
QUEUE = redis.StrictRedis()


def background_task():
    QUEUE.flushdb()

    url = app.config["SOCKETIO_REDIS_URL"]

    dir = os.path.dirname(__file__)
    filename1 = os.path.join(dir, "publish_stream.py")
    filename2 = os.path.join(dir, "setup_models.py")

    subprocess.Popen(["python", filename1, url, "0.1"])
    subprocess.Popen(["python", filename2, url])


@app.route("/")
def index():
    global THREAD
    if THREAD is None:
        THREAD = Thread(target=background_task, daemon=True)
        THREAD.start()

    return render_template("index.html", scene_url=url_for("get_scene"),
                                         scene_ready=SCENE_READY)


@app.route("/simulator/scene")
def get_scene():
    scene = ujson.loads(QUEUE.get("scene"))

    if scene is not None:
        global SCENE_READY
        SCENE_READY = True

    return jsonify(scene)
