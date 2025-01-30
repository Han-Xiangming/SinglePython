import os

CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
IMPORT_CHECK = "import"
EMPTY_LINE = ""
MULTILINE_KEYWORDS = {"if", "elif", "else", "for", "while", "def", "class"}

SinglePythonInfo = {
    "version": 0.90,
    "libs_warning": 1,
    "releases_version": "official",
    "importlibs": "os",
}
