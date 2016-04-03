from pymorse.stream import StreamJSON, PollThread
from json.decoder import JSONDecodeError
from flask_socketio import SocketIO

import time
import sys


def publish_stream(socketio, frequency=1):
    node_stream = StreamJSON("localhost", 65000)
    poll_thread = PollThread()

    poll_thread.start()

    while node_stream.is_up():
        node_stream.publish(["morseweb", {}])

        try:
            data = node_stream.get(timeout=1e-3) or node_stream.last()
        except JSONDecodeError:
            pass
        else:
            socketio.emit("simulator.update", data)

        time.sleep(frequency)


if __name__ == "__main__":
    message_queue, frequency = sys.argv[1:]
    publish_stream(SocketIO(message_queue=message_queue), float(frequency))
