import shutil
from pydub import AudioSegment
from pydub.utils import mediainfo
from pathlib import Path
import os
from rich.progress import track
from rich.console import Console

console = Console()

MP3_DUMP_PATH = Path.home() / 'Music' / 'mp3_dump'

class FileLocator():
    _found_file_paths = []
    _found_duplicates = 0

    def walk_dir(self, path, dump_path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_name = Path(file).name
                dest_file = f'{Path(file_name).stem}.mp3'
                if self.is_in_subdir(dump_path, dest_file):
                    # found_duplicates.append(os.path.abspath(os.path.join(root, file)))
                    # print(f'found duplicate file: {file}\nname match: {file_name} | {dest_file}\nskipping...')
                    self._found_duplicates += 1
                    continue
                else:
                    # yield os.path.abspath(os.path.join(root, file))
                    yield self._found_file_paths.append(os.path.abspath(os.path.join(root, file)))

    def is_in_subdir(self, path, file_name):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file_name == file:
                    return True
        return False
fl = FileLocator()

def user_confirm(question: str) -> bool:
    reply = str(input(question + ' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    elif reply[0] == 'n':
        return False
    else:
        new_question = question
        if 'please try again - ' not in question:
            new_question = f'please try again - {question}'
        return user_confirm(new_question)

def converter(dump_path):
    default_lib = open('default_library.txt', 'r+')
    library = ''
    if user_confirm('use path to library located in default_library.txt?'):
        library = default_lib.read()
        if library is None:
            library = input('no default path to library found. please provide path to library: ')
            default_lib.write(library)
    else:
        library = input('please provide path to library: ')
        default_lib.write(library)
    default_lib.close()

    file_count = 0
    with console.status('counting files...'):
        for _ in fl.walk_dir(library, dump_path):
            file_count += 1

    if fl._found_duplicates == 0 and fl._found_file_paths == []:
        print('no data found. are your paths correct?')
    elif fl._found_duplicates > 0 and fl._found_file_paths == []:
        print('no new files found. exiting dumper...')
    else:
        print(f'found {file_count} file(s). skipping {fl._found_duplicates} duplicate file(s)')
        for file_path in track(fl._found_file_paths, total=file_count, description='converting...'):
            file_name = Path(file_path).name
            dest_file = f'{Path(file_name).stem}.mp3'
            if file_name.endswith('.mp3'):
                shutil.copy2(file_path, os.path.abspath(os.path.join(dump_path, dest_file)))
            elif file_name.endswith('.wav'):
                AudioSegment.from_wav(file_path).export(os.path.abspath(os.path.join(dump_path, dest_file)), format='mp3', tags=mediainfo(file_path)['TAG'])
            elif file_name.endswith('.flac'):
                AudioSegment.from_file(file_path).export(os.path.abspath(os.path.join(dump_path, dest_file)), format='mp3', tags=mediainfo(file_path)['TAG'])
            else:
                print(f'found unsupported file: {file_name}')
        print(f'successfully dumped {file_count} file(s) into:\n{dump_path}\\')

converter(MP3_DUMP_PATH)