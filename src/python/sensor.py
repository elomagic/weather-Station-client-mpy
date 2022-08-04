# myapp.py - tbd.

import logging as log


class Sensor:

    i2c = None
    type = None

    def init(self, scl: Pin, sda: Pin):
        from machine import I2C
        import gc

        log.debug("Mem Alloc: {}".format(gc.mem_alloc()))
        log.debug("Mem Free: {}".format(gc.mem_free()))
        gc.collect()

        self.i2c = I2C(scl=scl, sda=sda)
        log.info('Scanning I2C bus for sensor...')
        addresses: list[int] = self.i2c.scan()

        log.info("adresses=%s" % addresses)

        if 0x76 in adresses:
            type = 0
        elif 0x40 in addresses:
            type = 1


    @staticmethod
    def __read_for_demo() -> dict:
        from random import getrandbits

        log.info('No sensor identified. Generate some random data for demonstration')

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

    def __read_si7021(self) -> dict:
        import driver_si7021

        try:
            log.info('Looking for SI7021...')
            si = driver_si7021.SI7021(self.i2c)
            log.info('Sensor SI7021 identified')
            return
        except Exception as ex:
            log.debug("SI7021 not found or unable to initialize: {}".format(ex))
            return None

        log.warn('SI7021 driver not implemented yet.')
        # Get temperature from si7021
        t = si.temperature()
        h = si.humidity()

        return {
            'temperature': t,
            'temperatureUnit': '°C',
            # "pressure": "{}.{:02d}".format(pi, pd),
            'pressureUnit': 'hPa',
            'humidity': h
            # "heatIndex":  = currentSensorData.heatIndex;
            # "heatIndexUnit":  = currentSensorData.heatIndexUnit;
            # "altitude":  = currentSensorData.altitude;
            # "altitudeUnit":  = currentSensorData.altitudeUnit;
        }

    def __read_bmp280(self) -> dict:
        import driver_bmp280

        try:
            log.info('Looking for BME/BMP280...')
            bmp = driver_bmp280.BME280(driver_bmp280.BME280_OSAMPLE_1, driver_bmp280.BME280_I2CADDR, self.i2c)
            log.info('Sensor BME/BMP280 identified')

            return
        except Exception as ex:
            log.debug("BMP280 not found or unable to initialize: {}".format(ex))
            return None


        t, p, h = bmp.read_compensated_data()

        p = p // 256
        pi = p // 100
        pd = p - pi * 100

        # print("***", self.bmp.values)

        result = {
            'temperature': "{}".format(t / 100),
            'temperatureUnit': '°C',
            'pressure': "{}.{:02d}".format(pi, pd),
            'pressureUnit': 'hPa',
            'humidity': h / 100
            # "heatIndex":  = currentSensorData.heatIndex;
            # "heatIndexUnit":  = currentSensorData.heatIndexUnit;
            # "altitude":  = currentSensorData.altitude;
            # "altitudeUnit":  = currentSensorData.altitudeUnit;
        }

        return result

    def read_sensor(self):
        if type == 0:
            return self.__read_bmp280()
        elif type == 1:
            return self.__read_si7021()
        else:
            return self.__read_for_demo()

    @staticmethod
    def print_data(sensor_data: dict):
        log.info("Temperature: {} {}, Heat index: {} {}, Pressure: {} {}, Altitude: {} {}, Humidity: {}%".format(
            sensor_data.get('temperature'), sensor_data.get('temperatureUnit'),
            sensor_data.get('heatIndex'), sensor_data.get('heatIndexUnit'),
            sensor_data.get('pressure'), sensor_data.get('pressureUnit'),
            sensor_data.get('altitude'), sensor_data.get('altitudeUnit'),
            sensor_data.get('humidity')
        ))
