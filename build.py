import os
import shutil
from src.version import APP_VER as VERSION

# I recommend to create a local symbolic link to the mpy-cross from the micropython project
# Sample: ln -s /Users/carsten/projects/micropython/mpy-cross/mpy-cross mpy-cross
_MPY_CROSS_FILE = './mpy-cross'

_PROJECT_DIR = '.'
_SOURCE_DIR = f'{_PROJECT_DIR}/src'
_TARGET_DIR = f'{_PROJECT_DIR}/target'
_DIST_DIR = f'{_TARGET_DIR}/dist'
_TARGET_FILES_DIR = f'{_DIST_DIR}/files'

if os.path.exists(_TARGET_DIR):
    shutil.rmtree(_TARGET_DIR)

if not os.path.exists(_TARGET_FILES_DIR):
    print(f'Creating folder {_TARGET_FILES_DIR}')
    os.makedirs(_TARGET_FILES_DIR)

# Copy src Python files to target files dir
shutil.copytree(_SOURCE_DIR, _TARGET_FILES_DIR, ignore=shutil .ignore_patterns('__pycache__', '*.pyc', 'tmp*'),  dirs_exist_ok=True)

print(f'Freezing Python files...')
for f in os.listdir(_TARGET_FILES_DIR):
    if f.endswith('.py'):
        source_file = f'{_TARGET_FILES_DIR}/{f}'
        target_file = f'{source_file[:-3]}.mpy'
        print(f'\tFreezing code of file {source_file} to {target_file}')
        if os.system(f'{_MPY_CROSS_FILE} {source_file}') != 0:
            raise RuntimeError(f'Unable to freeze code of file {source_file}')
        # Delete original py file
        os.remove(source_file)

shutil.copy(f'{_PROJECT_DIR}/requirements.txt', f'{_DIST_DIR}/requirements.txt')
shutil.copy(f'{_PROJECT_DIR}/Setup-Client.py', f'{_DIST_DIR}/Setup-Client.txt')

# Package target files
#version = '0.0.1-SNAPSHOT'
target_zip_file = f'{_TARGET_DIR}/weather-client-micropython {VERSION}'
print(f'Creating ZIP distribution file {target_zip_file}.zip...')
shutil.make_archive(target_zip_file, 'zip', _DIST_DIR)
print('Build done. Please check results.')
