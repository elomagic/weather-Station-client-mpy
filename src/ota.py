# Possible technical concept to work w/o TLS support
# Update phase must be confirmed manually by an user entered CRC to validate downloaded files

import os
from hashlib import sha256
from binascii import hexlify
import erequests as requests
import logging as log
import wifi
import configuration as c

UPDATE_PATH = '/update'


def url_encode(data: str) -> str:
    return data.replace('/', '%2F')


def __remove_folder(folder: str) -> bool:
    log.warn("Removing folder'{}'".format(folder))
    skip = False
    for file in os.ilistdir(folder):
        name = "{}/{}".format(folder, file[0])
        t = file[1]
        if t == 0x4000:
            skip = __remove_folder(name)
        elif c.FILENAME not in name:
            log.warn("Removing file {}".format(name))
            os.remove(name)
        else:
            skip = True

    if not skip and folder != '/' and folder != "/update":
        log.warn("Removing directory {}".format(folder))
        os.rmdir(folder)

    return skip


def __copy_file(source: str, target: str):
    log.warn("Copying file from '{}' to '{}'".format(source, target))
    with open(source, 'rb') as s:
        with open(target, 'wb') as t:
            buf = None
            while buf is None or len(buf) == 1024:
                buf = s.read(1024)
                t.write(buf)


def __copy_folder(folder: str):
    for file in os.ilistdir(folder):
        name = file[0]
        t = file[1]
        target_file = name[8:]
        if t == 0x4000:
            log.warn("Creating folder {}".format(target_file))
            os.mkdir(target_file)
            __copy_folder(name)
        elif c.FILENAME not in name:
            __copy_file(name, target_file)
        else:
            log.warn("Ignoring file {}".format(name))


def __create_folder(path: [str]):
    log.debug("Creating path '{}'".format(path))
    os.chdir('/')
    for folder in path:
        try:
            os.mkdir(folder)
        except Exception as e:
            log.debug("Folder '{}' seams already exists: {}".format(folder, e))

        os.chdir(folder)


def __download_file(file: str, hasher: sha256) -> sha256:
    log.warn("Downloading file {}".format(file))
    hasher.update(file)
    url = "{}/ota/update/{}".format(c.get_value(c.SERVER_URL), url_encode(file))
    target = "{}/{}".format(UPDATE_PATH, file)
    try:
        response: requests.Response = requests.get(url)
        try:
            http_code = response.status_code
            if (http_code >= 400) & (http_code < 600):
                log.warn("Unable to download file '{}'. HTTP code: {}".format(url, http_code))
                raise RuntimeError("Unable to download file '{}'. HTTP code: {}".format(url, http_code))

            __create_folder(target.split("/")[1:-1])

            with open(target, 'wb') as file:
                buf = response.raw.recv(1024)
                while buf:
                    hasher.update(buf)
                    file.write(buf)

                    buf = response.raw.recv(1024)
        finally:
            response.close()

    except Exception as e:
        log.error("Unable to download file from {} to {}: {}".format(url, target, e))
        raise

    return hasher


def __download_list() -> [str]:
    if not wifi.wlan.isconnected():
        raise RuntimeError('Not connected to the WLAN')

    url = "{}/ota/update".format(c.get_value(c.SERVER_URL))
    log.warn("Downloading update list from {} ".format(url))

    try:
        response = requests.get(url)
        log.debug("Respond content: {}".format(response.text))
        j = response.json()
        return j["files"]
    except Exception as e:
        log.error("Unable to get update list from {}: {}".format(url, e))
        raise


def update(crc: str = "demo"):
    wifi.start_client()

    # Clean update folder except the README.md
    __remove_folder(UPDATE_PATH)

    hasher = sha256()

    files: [str] = __download_list()

    # Iterate list and download files
    for file in files:
        hasher = __download_file(file, hasher)

    h = str(hexlify(hasher.digest()))

    # Check CRC of all files against users entered CRC. When fail delete uploaded files.
    if h != crc:
        __remove_folder(UPDATE_PATH)
        raise RuntimeError("SHA256 file check of downloaded files. Failed. Expected={} != Calculated={}".format(crc, h))

    log.warn('Download successful. Continue with "upgrade()".')


def upgrade():

    wifi.start_client()
    # Remove all files except file "ota.py" and folder "logs" and update".
    __remove_folder('/')

    # Copy all files from folder "update" to root folder
    __copy_folder(UPDATE_PATH)

    # Reboot ESP
    log.warn('Upgrade seams successful. Reboot hardware')
    from machine import reset
    reset()
