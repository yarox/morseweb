from morse.services.supervision_services import get_obj_by_name
from morse.helpers.components import add_data
from morse.core.services import service
from morse.core import blenderapi

import morse.core.sensor
import logging
import time


logger = logging.getLogger("morse." + __name__)


class ExtraServices(morse.core.sensor.Sensor):
    """
    Extra services needed by morseweb.
    """
    _name = "ExtraServices"
    _short_desc = "Extra services needed by morseweb"

    add_data("start_time", 0.0, "float", "Simulation start time")
    add_data("realitime", 0.0, "float", "Elapsed real time")
    add_data("simtime", 0.0, "float", "Elapsed simulation time")

    def __init__(self, obj, parent=None):
        logger.info("%s initialization" % obj.name)

        morse.core.sensor.Sensor.__init__(self, obj, parent)
        self.local_data["start_time"] = time.time()

        logger.info('Component initialized')

    @service
    def get_start_time(self):
        """
        Get the simulation start time. :returns: the time in seconds since the
        epoch as a floating point number.
        """
        start_time = self.local_data['start_time']
        return start_time

    @service
    def get_environment(self):
        """
        Get the current environment name.
        """
        ssh = blenderapi.bpy.data.objects['Scene_Script_Holder']
        return ssh.game.properties['environment_file'].value

    @service
    def get_camera_position(self):
        """
        Get the CamaraFP (MORSE' environment camera) world position. [x, y, z]
        :returns: The camera's world position. [x, y, z].
        """
        blender_object = get_obj_by_name('CameraFP')
        return blender_object.worldPosition.to_tuple()

    def default_action(self):
        """
        Update elapsed time.
        """
        self.local_data['realitime'] = time.time() * 1000.0
        self.local_data['simtime'] = self.local_data['timestamp']
