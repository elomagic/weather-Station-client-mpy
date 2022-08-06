import os
import shutil

_MPY_CROSS_FILE = 'mpy-cross'

_SOURCE_DIR = './src'
_TARGET_DIR = './target'
_TARGET_FILES_DIR = f'{_TARGET_DIR}/files'

if os.path.exists(_TARGET_DIR):
    shutil.rmtree(_TARGET_DIR)

if not os.path.exists(_TARGET_FILES_DIR):
    print(f'Creating folder {_TARGET_FILES_DIR}')
    os.makedirs(_TARGET_FILES_DIR)

# Copy src python files to target files dir
shutil.copytree(_SOURCE_DIR, _TARGET_FILES_DIR, dirs_exist_ok=True)

for f in os.listdir(_TARGET_FILES_DIR):
    if f.endswith('.py'):
        source_file = f'{_TARGET_FILES_DIR}/{f}'
        target_file = f'{source_file[:-3]}.mpy'
        print(f'Freezing code of file {source_file} to {target_file}')
        if os.system(f'{_MPY_CROSS_FILE} {source_file}') != 0:
            raise RuntimeError(f'Unable to freeze code of file {source_file}')
        # Delete original py file
        os.remove(source_file)

# Package target files
version = '0.0.1-SNAPSHOT'
target_zip_file = f'weather-client-micropython {version}.zip'
shutil.make_archive(target_zip_file, 'zip', _TARGET_FILES_DIR)
print('Build done. Please check results.')
