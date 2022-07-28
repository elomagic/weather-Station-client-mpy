import client


def test_post_weather_data():
    data = {
        'temperature': '20.5',
        'pressure': '1024',
        'humidity': '68'
    }

    client.post_weather_data("localhost:41883", data)
