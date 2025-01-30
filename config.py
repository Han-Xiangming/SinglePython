import os

CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
IMPORT_CHECK = "import"
EMPTY_LINE = ""

SinglePythonInfo = {
    "version": 0.92,
    "libs_warning": 1,
    "releases_version": "official",
    "importlibs": "os",
}
