import logging as log
from machine import Pin, I2C


def read_sensor():
    import gc
    import board

    log.debug("Mem Alloc: {}".format(gc.mem_alloc()))
    log.debug("Mem Free: {}".format(gc.mem_free()))
    gc.collect()

    i2c = I2C(scl=board.SCL_PIN, sda=board.SDA_PIN)
    log.info('Scanning I2C bus for sensor...')
    addresses = i2c.scan()

    log.info("Done")
    log.info("adresses=%s" % addresses)

    if 0x76 in addresses:
        log.info('Sensor BME/BMP280 identified')
        return _read_bmp280()
    elif 0x40 in addresses:
        log.info('Sensor SI7021 identified')
        return _read_si7021()
    else:
        log.info('No sensor identified. Generate some random data for demonstration')
        return _read_for_demo()


def _read_for_demo() -> dict:
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

def _read_si7021(i2c: I2C) -> dict:
    import driver_si7021

    try:
        # log.info('Looking for SI7021...')
        si = driver_si7021.SI7021(i2c)
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


def _read_bmp280(i2c: I2C) -> dict:
    import driver_bmp280

    try:
        bmp = driver_bmp280.BME280(driver_bmp280.BME280_OSAMPLE_1, driver_bmp280.BME280_I2CADDR, i2c)
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


def print_data(sensor_data: dict):
    log.info("Temperature: {} {}, Heat index: {} {}, Pressure: {} {}, Altitude: {} {}, Humidity: {}%".format(
        sensor_data.get('temperature'), sensor_data.get('temperatureUnit'),
        sensor_data.get('heatIndex'), sensor_data.get('heatIndexUnit'),
        sensor_data.get('pressure'), sensor_data.get('pressureUnit'),
        sensor_data.get('altitude'), sensor_data.get('altitudeUnit'),
        sensor_data.get('humidity')
    ))
