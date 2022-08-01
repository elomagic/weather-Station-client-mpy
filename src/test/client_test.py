import client
import wifi
import configuration as c


def test_post_weather_data():
    data = {
        'temperature': '20.5',
        'pressure': '1024',
        'humidity': '68'
    }

    client.post_weather_data(c.get_value(c.SERVER_URL), data)


def test():
    wifi.start_client()

    test_post_weather_data()
