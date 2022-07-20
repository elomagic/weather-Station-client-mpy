# myapp.py - tbd.

import driver_bmp280
import driver_si7021
import logging as log


class Sensor:

    bmp = None
    si = None

    def init(self, scl, sda):
        from machine import I2C

        log.info('Identifying sensor...')
        i2c = I2C(scl=scl, sda=sda)

        try:
            self.bmp = driver_bmp280.BME280(driver_bmp280.BME280_OSAMPLE_1, driver_bmp280.BME280_I2CADDR, i2c)
            log.info('Sensor BME/BMP280 identified')

            return
        except Exception as ex:
            log.debug("BMP280 not found or unable to initialize: {}".format(ex))

        try:
            self.si = driver_si7021.SI7021(i2c)
            log.info('Sensor SI7021 identified')
            return
        except Exception as ex:
            log.debug("SI7021 not found or unable to initialize: {}".format(ex))

        log.info('No sensor identified. Generate some random data for demonstration')

    @staticmethod
    def __read_for_demo():
        from random import getrandbits

        return {
            'temperature': 20 + getrandbits(3),
            'temperatureUnit': '°C',
            "pressure": 998 + getrandbits(5),
            'pressureUnit': 'hPa',
            'humidity': 50 + getrandbits(5),
            # "heatIndex":  = currentSensorData.heatIndex;
            # "heatIndexUnit":  = currentSensorData.heatIndexUnit;
            # "altitude":  = currentSensorData.altitude;
            # "altitudeUnit":  = currentSensorData.altitudeUnit;
        }

    def __read_si7021(self):
        log.warn('SI7021 driver not implemented yet.')
        # Get temperature from si7021
        t = self.si.temperature()
        h = self.si.humidity()

        return {
            'temperature': t,
            'temperatureUnit': 'C',
            # "pressure": "{}.{:02d}".format(pi, pd),
            'pressureUnit': 'hPa',
            'humidity': h
            # "heatIndex":  = currentSensorData.heatIndex;
            # "heatIndexUnit":  = currentSensorData.heatIndexUnit;
            # "altitude":  = currentSensorData.altitude;
            # "altitudeUnit":  = currentSensorData.altitudeUnit;
        }

    def __read_bmp280(self):
        t, p, h = self.bmp.read_compensated_data()

        p = p // 256
        pi = p // 100
        pd = p - pi * 100

        # print("***", self.bmp.values)

        result = {
            'temperature': "{}".format(t / 100),
            'temperatureUnit': 'C',
            'pressure': "{}.{:02d}".format(pi, pd),
            'pressureUnit': 'hPa',
            'humidity': h
            # "heatIndex":  = currentSensorData.heatIndex;
            # "heatIndexUnit":  = currentSensorData.heatIndexUnit;
            # "altitude":  = currentSensorData.altitude;
            # "altitudeUnit":  = currentSensorData.altitudeUnit;
        }

        return result

    def read_sensor(self):
        if self.bmp is not None:
            return self.__read_bmp280()
        elif self.si is not None:
            return self.__read_si7021()

        return self.__read_for_demo()

    @staticmethod
    def print_data(sensor_data):
        log.info("Temperature: {} {}, Heat index: {} {}, Pressure: {} {}, Altitude: {} {}, Humidity: {}%".format(
            sensor_data.get('temperature'), sensor_data.get('temperatureUnit'),
            sensor_data.get('heatIndex'), sensor_data.get('heatIndexUnit'),
            sensor_data.get('pressure'), sensor_data.get('pressureUnit'),
            sensor_data.get('altitude'), sensor_data.get('altitudeUnit'),
            sensor_data.get('humidity')
        ))
