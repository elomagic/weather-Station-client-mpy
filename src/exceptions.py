# exceptions.py - All customized exceptions

class BaseError(Exception):
    message = 'Unexpected error occurred.'
    flashCount = 6


class WlanNotConnectedError(BaseError):
    message = 'Wifi currently not connected to access point. Caching weather data for next post.'
    flashCount = 3


class UnableToPostError(BaseError):
    message = 'Unable to post data to server.'
    flashCount = 4


class ReadNtpError(BaseError):
    message = 'Failed.'
    flashCount = 5
