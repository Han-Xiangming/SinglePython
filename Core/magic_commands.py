# magic_commands.py

import io
import math
import re
import sys
import time
import difflib
from contextlib import redirect_stdout, redirect_stderr
from timeit import Timer
from typing import Any, Dict, Callable
from dataclasses import dataclass
from tqdm import tqdm

from Core.utils import color_print

class TimeFormatter:
    """
    时间格式化工具，支持多种单位自动转换。
    """
    @staticmethod
    def format_time(timespan: float, precision: int = 3) -> str:
        """
        格式化时间间隔为可读字符串。
        """
        if timespan < 0:
            return f"-{TimeFormatter._format_positive_time(abs(timespan), precision)}"
        elif timespan == 0:
            return "0s"
        else:
            return TimeFormatter._format_positive_time(timespan, precision)

    # μ支持性缓存为类变量
    _HAS_MICRO_SIGN = None

    @staticmethod
    def _format_positive_time(timespan: float, precision: int) -> str:
        """
        高效地将秒数转为人类可读字符串，支持自动单位转换。
        优化点：
        - 大于60秒直接用divmod批量拆解，避免多余循环。
        - 小于60秒用数量级直接定位单位。
        - μ支持性只检测一次。
        - 字符串拼接用生成器和join。
        """
        if timespan >= 60.0:
            d, rem = divmod(timespan, 86400)
            h, rem = divmod(rem, 3600)
            m, s = divmod(rem, 60)
            parts = []
            if d >= 1:
                parts.append(f'{int(d)}d')
            if h >= 1:
                parts.append(f'{int(h)}h')
            if m >= 1:
                parts.append(f'{int(m)}min')
            if s > 0 or not parts:
                # s可能是浮点数，按精度保留
                s_str = f'{s:.{precision}g}' if s % 1 else str(int(s))
                parts.append(f'{s_str}s')
            return " ".join(parts)

        # μ单位支持性只检测一次
        if TimeFormatter._HAS_MICRO_SIGN is None:
            try:
                if hasattr(sys.stdout, "encoding") and sys.stdout.encoding:
                    "μ".encode(sys.stdout.encoding)
                    TimeFormatter._HAS_MICRO_SIGN = True
                else:
                    TimeFormatter._HAS_MICRO_SIGN = False
            except Exception:
                TimeFormatter._HAS_MICRO_SIGN = False
        units = ["s", "ms", "μs" if TimeFormatter._HAS_MICRO_SIGN else "us", "ns"]
        scaling = [1, 1e3, 1e6, 1e9]

        if timespan > 0.0:
            order = min(max(int(-math.log10(timespan) // 3), 0), 3)
        else:
            order = 3
        value = timespan * scaling[order]
        return f"{value:.{precision}g} {units[order]}"

# --------- 魔法命令自动注册机制 ---------
@dataclass(frozen=True)
class MagicCommand:
    func: Callable
    doc: str

MAGIC_COMMANDS: Dict[str, MagicCommand] = {}

def magic_command(name):
    """装饰器：自动注册魔法命令并收集docstring"""
    def decorator(func):
        doc = (func.__doc__ or '').strip().splitlines()
        MAGIC_COMMANDS[name] = MagicCommand(func=func, doc=doc[0] if doc else '')
        return func
    return decorator

class MagicCommandHandler:
    __slots__ = ("shell",)
    def __init__(self, shell):
        self.shell = shell

    def handle_magic_command(self, text):
        """解析并分发魔法命令，支持模糊匹配建议，正则解析参数"""
        match = re.match(r'^(%\w+)(?:\s+(.*))?$', text.strip())
        if not match:
            print(color_print('Invalid magic command format.', 'red'))
            return
        cmd, arg = match[1], match[2] or ""
        if magic := MAGIC_COMMANDS.get(cmd):
            return magic.func(self, arg)
        if close := difflib.get_close_matches(cmd, MAGIC_COMMANDS.keys(), n=1):
            print(color_print(f"Unknown magic command: {cmd}. Did you mean {close[0]}?", 'yellow'))
        else:
            self.handle_unknown_command(cmd)

    def handle_unknown_command(self, command):
        print(f"Unknown magic command: {command}")

    @magic_command("%time")
    def handle_time_command(self, code_to_time: str) -> None:
        """
        计时执行代码块。
        """
        if not code_to_time:
            print(f"{color_print('Usage:', 'yellow')} %time <python_code>")
            return
        self.execute_timed_code(code_to_time)

    def execute_timed_code(self, code_to_time: str = None) -> None:
        """
        实际执行计时代码，抑制所有输出。
        """
        local_vars = self.shell.interpreter.locals
        def run():
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exec(code_to_time, local_vars)
        timer = Timer(run)
        start = time.perf_counter()
        try:
            timer.timeit(number=1)
        except Exception as e:
            print(color_print(f"Exception: {e}", "red"))
            return
        end = time.perf_counter()
        elapsed = end - start
        print(f"Elapsed time: {TimeFormatter.format_time(elapsed)}")

    @magic_command("%timeit")
    def handle_timeit_command(self, code_to_time: str) -> None:
        """
        多次计时执行代码块，统计最佳/平均/最差。
        """
        if not code_to_time:
            print(f"{color_print('Usage:', 'yellow')} %timeit <python_code>")
            return
        self.execute_timeit_code(5, 3, code_to_time)

    def execute_timeit_code(self, n: int, r: int, code_to_time: str = None) -> None:
        """
        实际执行多次计时代码，抑制所有输出。
        """
        local_vars = self.shell.interpreter.locals
        def run():
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                exec(code_to_time, local_vars)
        timer = Timer(run)
        try:
            times = timer.repeat(repeat=r, number=n)
        except Exception as e:
            print(color_print(f"Exception: {e}", "red"))
            return
        best = min(times) / n
        worst = max(times) / n
        avg = sum(times) / (n * r)
        print(f"Best: {TimeFormatter.format_time(best)}; "
              f"Avg: {TimeFormatter.format_time(avg)}; "
              f"Worst: {TimeFormatter.format_time(worst)}")

    @magic_command("%who")
    def handle_who_command(self, arg: str = "") -> None:
        """
        显示当前会话下所有用户变量名。
        """
        local_vars = self.shell.interpreter.locals
        user_vars = (k for k in local_vars if not k.startswith("__") and not callable(local_vars[k]))
        if user_vars_list := list(user_vars):
            print("User variables:", ", ".join(user_vars_list))
        else:
            print("No user variables defined.")

    @magic_command("%whos")
    def handle_whos_command(self, arg: str = "") -> None:
        """
        显示当前会话下所有用户变量及其值。
        """
        local_vars = self.shell.interpreter.locals
        user_vars = ((k, v) for k, v in local_vars.items() if not k.startswith("__") and not callable(v))
        if user_vars_list := list(user_vars):
            print("User variables and values:")
            for k, v in user_vars_list:
                print(f"  {k}: {repr(v)}")
        else:
            print("No user variables defined.")

    @magic_command("%ls")
    def handle_ls_command(self, arg: str = "") -> None:
        """
        列出当前目录下的文件和目录。
        """
        import os
        from Core.utils import color_print, Color

        cwd = os.getcwd()
        all_items = os.listdir(cwd)
        dirs = sorted([f for f in all_items if os.path.isdir(os.path.join(cwd, f))], key=lambda x: (x.startswith('.'), x.lower()))
        files = sorted([f for f in all_items if not os.path.isdir(os.path.join(cwd, f))], key=lambda x: (x.startswith('.'), x.lower()))

        def style_name(f, is_dir):
            if is_dir:
                return color_print(f, Color.BLUE)
            elif f.startswith('.'):
                return color_print(f, Color.WHITE)
            else:
                return f

        for d in dirs:
            print(style_name(d, True))
        for f in files:
            print(style_name(f, False))

    @magic_command("%pwd")
    def handle_pwd_command(self, arg: str = "") -> None:
        """
        显示当前工作目录。
        """
        import os
        print(f"Current working directory: {os.getcwd()}")

    @magic_command("%help")
    def handle_help_command(self, arg: str = "") -> None:
        """
        显示所有可用魔法命令。
        """
        print("Available magic commands:")
        for cmd in sorted(MAGIC_COMMANDS.keys()):
            if doc := MAGIC_COMMANDS[cmd].doc:
                print(f"  {cmd:8} - {doc}")
            else:
                print(f"  {cmd}")

