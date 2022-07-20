#!/usr/bin/env python

import os
import sys


def contains_option(args, option):
    """Returns true when option in list of args. Otherwise false"""
    return option in args


def get_value_of_option(args, option, default_value=None):
    """Returns value of option when in list of args. Otherwise default value. By default, default value is None."""
    if not contains_option(args, option):
        return default_value

    return args[args.index(option) + 1]


def create_template(file):
    template = '''# SSID of the access point
wifi.ssid=ssid
# Password of the access point
wifi.password=changeit
# IP address of this client when access point doesn't provide dynamically IP address. Usually empty
wifi.address=
# Usually empty
wifi.netmask=255.255.255.0
# Usually empty
wifi.gateway=
# Usually empty
wifi.dns=8.8.8.8
# Name of client bot
wifi.clientName=[BOT_NAME]

# Unique identifier of this client ( Looking for a generator. See https://www.uuidgenerator.net/version4 )
sensor.uid=uuid
# Measure interval in seconds
sensor.measureInterval=60

# URL server address. Sample "http://192.168.150.2/rest" 
server.url=http://[HOSTNAME]/rest
# Application key to authentication
server.appKey=
'''

    with open(file, 'w') as f:
        f.write(template)


def print_help():
    print("Usage: Setup-Client.py COMMAND [OPTIONS]\n")
    print("  Tool for setup connected ESP\n")
    print("Commands:")
    print("  write  Write the configuration file to the bot")
    print("  create Creates a configuration template\n")
    print("  read   Retrieve configuration from bot\n")
    print("Options:")
    print("  -p, --port PORT    Name of serial port for connected board.  Can optionally")
    print("                     specify with AMPY_PORT environment variable.  [required]")
    print("  -b, --baud BAUD    Baud rate for the serial connection (default 115200).")
    print("                     Can optionally specify with AMPY_BAUD environment")
    print("                     variable.")
    print("  -f, --file         Name of the configuration file.  (default 'weather-client-configuration.json)")
    print("  --reset            Do a hard reset after configuration successful written.")
    print("  --help             Show this message and exit.")


if contains_option(sys.argv, '--help'):
    print_help()
else:
    port = get_value_of_option(sys.argv, '--port', get_value_of_option(sys.argv, '-p', 'COM7'))
    baud = get_value_of_option(sys.argv, '--baud', get_value_of_option(sys.argv, '-b', '115200'))
    sourceFile = get_value_of_option(sys.argv, '--file', get_value_of_option(sys.argv, '-f', 'weather-client'
                                                                                             'configuration.properties'))
    reset = contains_option(sys.argv, '--reset')

    command = sys.argv[1]

    if command == 'create':
        create_template(sourceFile)
    elif command == 'read':
        print(f'Retrieve configuration \'{sourceFile}\' from {port}...')
        os.system(f'ampy --port {port} --baud {baud} get configuration {sourceFile}')
    elif command == 'write':
        print(f'Deploying configuration \'{sourceFile}\' to {port}...')
        os.system(f'ampy --port {port} --baud {baud} put {sourceFile} configuration')

        if reset:
            os.system(f'ampy --port {port} --baud {baud} reset')

    else:
        print(f'Unsupported command \'{command}.')


