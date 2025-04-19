# utils.py

import platform
import os
from functools import lru_cache
from enum import Enum
from typing import Union, Dict

from colorama import Fore, Style, init

from Core.config import SinglePythonInfo

init(autoreset=True)  # 自动重置颜色，防止串色

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'
    CYAN = 'cyan'
    WHITE = 'white'

COLOR_MAP: Dict[str, str] = {
    'red': Fore.RED,
    'green': Fore.GREEN,
    'yellow': Fore.YELLOW,
    'blue': Fore.BLUE,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE,
}

def color_print(text: str, color: Union[str, Color]) -> str:
    """
    返回带颜色的字符串，未识别颜色则原样输出。支持Enum和字符串。
    :param text: 需要着色的文本
    :param color: 颜色名或Color枚举
    :return: 着色后的字符串
    """
    color_key = color.value if isinstance(color, Color) else str(color).lower()
    color_code = COLOR_MAP.get(color_key, "")
    return f"{color_code}{text}{Style.RESET_ALL}" if color_code else text


@lru_cache(maxsize=1)
def get_version() -> str:
    """
    获取当前 SinglePython 及 Python 版本信息。
    :return: 版本信息字符串
    """
    return (
        f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}, "
        f"By Python {platform.python_version()}"
    )


def show_startup_info(version_info: dict) -> None:
    """
    打印启动欢迎信息。
    :param version_info: 包含版本和发布信息的字典
    """
    sp_version = f"SinglePython {version_info['version']}-{version_info['releases_version']}"
    py_version = platform.python_version()
    env_info = f" [Running on {platform.platform()} {platform.version()}]"
    welcome_message = f"{sp_version} (Python Version: {py_version}) {env_info}"
    print(color_print(welcome_message, "cyan"))


def handle_exception(exception: Exception, msg_prefix: str) -> None:
    """
    统一异常输出，带红色高亮。
    :param exception: 异常对象
    :param msg_prefix: 前缀信息
    """
    print(f"{color_print(f'{msg_prefix}:', 'red')} {exception}")


# 文件内容缓存，提升为全局（或用lru_cache）
@lru_cache(maxsize=16)
def _get_file_content(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def execute_code_from_file(filename: str) -> None:
    """
    执行指定文件中的 Python 代码，带全局缓存和异常处理。
    :param filename: 文件路径
    """
    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File {filename} not found")
        code_content = _get_file_content(filename)
        if not code_content.strip():
            print(f"{color_print('SinglePython Warning:', Color.MAGENTA)} {filename} is empty")
            return
        codes = compile(code_content, filename, "exec")
        exec(codes, {}, {})  # 受控命名空间，避免污染全局
        print(f"{color_print('SinglePython Info:', Color.MAGENTA)} {filename} executed successfully")
    except Exception as e:
        handle_exception(e, "SinglePython Error")