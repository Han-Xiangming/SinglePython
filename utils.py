import os
import platform
from functools import lru_cache

from colorama import Fore, Style, init

from config import SinglePythonInfo

init()

@lru_cache(maxsize=1)
def get_version():
    return f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}, By Python {platform.python_version()}"

def show_startup_info(version_info):
    sp_version = f"SinglePython {version_info['version']}-{version_info['releases_version']}"
    py_version = platform.python_version()
    env_info = f" [Running on {platform.platform()} {platform.version()}]"
    welcome_message = f"{sp_version} (Python Version: {py_version}) {env_info}"
    print(color_print(welcome_message, "cyan"))

def color_print(text, color):
    color_dict = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }
    return f"{color_dict.get(color, '')}{text}{Style.RESET_ALL}"


def execute_code_from_file(filename: str) -> None:
    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File {filename} not found")
        with open(filename, "r", encoding="utf-8") as f:
            code_content = f.read()
        if not code_content.strip():
            print(f"{color_print('SinglePython Warning:', 'magenta')} {filename} is empty")
            return
        codes = compile(code_content, filename, "exec")
        exec(codes)
        print(f"{color_print('SinglePython Info:', 'magenta')} {filename} executed successfully")
    except Exception as e:
        handle_exception(e, "SinglePython Error")

def handle_exception(e, message_prefix):
    print(f"{color_print(f'{message_prefix}:', 'red')} {e}")
