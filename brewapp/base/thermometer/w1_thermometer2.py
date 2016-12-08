import os
import re
import sys
from brewapp import app
from subprocess import call


class OneWireThermometer2(object):
    AVERAGE_SENSOR_ID = "average"
    MAX_SENSOR_ID = "maximum"

    def init(self):
        try:
            call(["modprobe", "w1-gpio"])
            call(["modprobe", "w1-therm"])
        except Exception as e:
            app.logger.error(
                "Failed to initialize 1 wire thermometer ERROR: " + str(e))

    def getSensors(self):
        try:
            arr = self.__listW1Sensors()
            arr.extend([self.AVERAGE_SENSOR_ID, self.MAX_SENSOR_ID])
            return arr
        except:
            return ["1WDummySensor1", "1WDummySensor2"]

    def readTemp(self, tempSensorId):
        if tempSensorId == self.AVERAGE_SENSOR_ID:
            return self.__getAverageTemp()
        elif tempSensorId == self.MAX_SENSOR_ID:
            return self.__getMaxTemp()
        else:
            return self.__getSensorValue(tempSensorId)

    def __listW1Sensors(self):
        arr = []
        for dirname in os.listdir('/sys/bus/w1/devices'):
            if(dirname.startswith("28") or dirname.startswith("10")):
                arr.append(dirname)
        return arr

    def __getSensorValue(self, tempSensorId):
        value = None
        path = "/sys/bus/w1/devices/w1_bus_master1/" + tempSensorId + "/w1_slave"

        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value = float(m.group(2)) / 1000.0
            f.close()
        except Exception as e:
            app.logger.warning("Read temp failed " + str(e))

        return value

    def __getAverageTemp(self):
        value = 0
        count = 0
        for sensor in self.__listW1Sensors():
            value += self.__getSensorValue(sensor)
            count += 1

        if count == 0:
            return 0
        else:
            return value / count

    def __getMaxTemp(self):
        value = sys.float_info.min

        for sensor in self.__listW1Sensors():
            tmp = self.__getSensorValue(sensor)
            if tmp > value:
                value = tmp

        return value

