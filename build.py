#!/usr/bin/env python

import os
import sys
import shutil
from src.python.version import APP_VER as VERSION

# I recommend to create a local symbolic link to the mpy-cross compiled binary from the micropython project
# Sample: ln -s /Users/carsten/projects/micropython/mpy-cross/mpy-cross mpy-cross
_MPY_CROSS_FILE = './mpy-cross'

_PROJECT_DIR = '.'
_SOURCE_DIR = f'{_PROJECT_DIR}/src/python'
_TARGET_DIR = f'{_PROJECT_DIR}/target'
_DIST_DIR = f'{_TARGET_DIR}/dist'
_TARGET_FILES_DIR = f'{_DIST_DIR}/files'


def contains_option(args: [], option: str) -> bool:
    """Returns true when option in list of args. Otherwise false"""
    return option in args


def get_value_of_option(args: [], option: str, default_value=None) -> str:
    """Returns value of option when in list of args. Otherwise default value. By default, default value is None."""
    if not contains_option(args, option):
        return default_value

    return args[args.index(option) + 1]


def clean() -> None:
    global _TARGET_DIR

    print('\n-------- CLEAN --------')

    if os.path.exists(_TARGET_DIR):
        print(f'Cleaning folder {_TARGET_DIR}')
        shutil.rmtree(_TARGET_DIR)

    os.makedirs(_TARGET_DIR)

    print('Done.')


def resources() -> None:
    global _TARGET_FILES_DIR
    global _SOURCE_DIR

    print('\n-------- RESOURCES --------')

    if not os.path.exists(_TARGET_FILES_DIR):
        print(f'Creating folder {_TARGET_FILES_DIR}')
        os.makedirs(_TARGET_FILES_DIR)

    # Copy src Python files to target files dir
    print(f'Copying files from \'{_SOURCE_DIR}\' to \'{_TARGET_FILES_DIR}\'')
    shutil.copytree(
        _SOURCE_DIR,
        _TARGET_FILES_DIR,
        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'tmp*'),
        dirs_exist_ok=True)

    print('Done.')


def build() -> None:
    global _TARGET_FILES_DIR
    global _MPY_CROSS_FILE

    print('\n-------- BUILD --------')

    print(f'Freezing Python files...')
    for f in os.listdir(_TARGET_FILES_DIR):
        if f == 'main.py':
            continue

        if f.endswith('.py'):
            source_file = f'{_TARGET_FILES_DIR}/{f}'
            target_file = f'{source_file[:-3]}.mpy'
            print(f'\tFreezing code of file {source_file} to {target_file}')
            if os.system(f'{_MPY_CROSS_FILE} {source_file}') != 0:
                raise RuntimeError(f'Unable to freeze code of file {source_file}')
            # Delete original py file
            os.remove(source_file)

    print('Done.')


def package() -> None:
    global _PROJECT_DIR
    global _DIST_DIR

    print('\n-------- PACKAGE --------')

    shutil.copy(f'{_PROJECT_DIR}/requirements.txt', f'{_DIST_DIR}/requirements.txt')
    shutil.copy(f'{_PROJECT_DIR}/Setup-Client.py', f'{_DIST_DIR}/Setup-Client.txt')

    # Package target files
    target_zip_file = f'{_TARGET_DIR}/weather-client-micropython {VERSION}'
    print(f'Creating ZIP distribution file {target_zip_file}.zip...')
    shutil.make_archive(target_zip_file, 'zip', _DIST_DIR)

    print('Done.')


def deploy() -> None:
    global _TARGET_FILES_DIR

    print('\n-------- DEPLOY --------')

    port = get_value_of_option(sys.argv, '--port', get_value_of_option(sys.argv, '-p', 'COM7'))
    baud = get_value_of_option(sys.argv, '--baud', get_value_of_option(sys.argv, '-b', '115200'))

    root = _TARGET_FILES_DIR
    print(f'Deploying folder \'{_TARGET_FILES_DIR}\' to {port}...')
    for current_dir, subdirs, files in os.walk(_TARGET_FILES_DIR):
        # Map source root to target folder
        target_dir = f'/{current_dir[len(root)+1:]}'

        for file in files:
            source_file = os.path.join(current_dir, file)
            target_file = os.path.join(target_dir, file)
            print(f'\tDeploying file \'{source_file}\' to \'{target_file}\'...')
            if os.system(f'ampy --port {port} --baud {baud} put {source_file} {target_file}') != 0:
                raise IOError('Unable to deploy files')

    print('Done.')


clean_switch: bool = contains_option(sys.argv, 'clean')
resources_switch: bool = contains_option(sys.argv, 'resources')
build_switch: bool = contains_option(sys.argv, 'build')
package_switch: bool = contains_option(sys.argv, 'package')
deploy_switch: bool = contains_option(sys.argv, 'deploy')

build_switch = build_switch or not (clean_switch or resources_switch or build_switch or package_switch or deploy_switch)

if clean_switch or build_switch or resources_switch:
    clean()

if resources_switch or build_switch:
    resources()

if build_switch:
    build()

if package_switch or build_switch:
    package()

if deploy_switch:
    deploy()

print('\nBuild script done. Please check results.')
