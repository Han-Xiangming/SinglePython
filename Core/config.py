# config.py
import os

SinglePythonInfo = {'version': '0.93',
                    'libs_warning': '1',
                    'releases_version': 'official',
                    'importlibs': 'os',
                    'clear_command': "cls" if os.name == "nt" else "clear"}
