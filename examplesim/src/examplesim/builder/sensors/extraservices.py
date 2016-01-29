from morse.builder.creator import SensorCreator

class ExtraServices(SensorCreator):
    def __init__(self, name=None):
        SensorCreator.__init__(self, name, \
                               "examplesim.sensors.extraservices.ExtraServices",\
                               "ExtraServices")
