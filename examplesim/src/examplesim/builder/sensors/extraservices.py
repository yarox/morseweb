from morse.builder.creator import SensorCreator

class ExtraServices(SensorCreator):
    _classpath = "examplesim.sensors.extraservices.ExtraServices"
    _blendname = "extraservices"

    def __init__(self, name=None):
        SensorCreator.__init__(self, name)
