from flask_socketio import SocketIO
from flask import Flask

import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.config.from_object('morseweb.default_settings')
app.config.from_envvar('MORSEWEB_SETTINGS', silent=True)

socketio = SocketIO(app, async_mode="eventlet",
                    message_queue=app.config["SOCKETIO_REDIS_URL"])


import morseweb.views
