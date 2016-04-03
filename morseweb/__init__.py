from flask_socketio import SocketIO
from flask import Flask

import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.config["DEBUG"] = False
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SOCKETIO_REDIS_URL"] = "redis://localhost:6379/0"

socketio = SocketIO(app, async_mode="eventlet",
                    message_queue=app.config["SOCKETIO_REDIS_URL"])


import morseweb.views
