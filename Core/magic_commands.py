import io
import math
import re
import sys
import time
from contextlib import redirect_stdout, redirect_stderr
from timeit import Timer

from tqdm import tqdm

from Core.utils import color_print


class TimeFormatter:
    @staticmethod
    def format_time(timespan, precision=3):
        if timespan < 0:
            return "-" + TimeFormatter._format_positive_time(abs(timespan), precision)
        elif timespan == 0:
            return "0s"
        else:
            return TimeFormatter._format_positive_time(timespan, precision)

    @staticmethod
    def _format_positive_time(timespan, precision):
        if timespan >= 60.0:
            parts = [("d", 60 * 60 * 24), ("h", 60 * 60), ("min", 60), ("s", 1)]
            time_parts = []
            leftover = timespan
            for suffix, length in parts:
                value = int(leftover / length)
                if value > 0:
                    leftover = leftover % length
                    time_parts.append(f'{value}{suffix}')
                if math.isclose(leftover, 0, abs_tol=1e-9):
                    break
            return " ".join(time_parts)

        units = ["s", "ms", "us", "ns"]
        try:
            if hasattr(sys.stdout, "encoding") and sys.stdout.encoding:
                "μ".encode(sys.stdout.encoding)
                units = ["s", "ms", "μs", "ns"]
        except (AttributeError, LookupError):
            pass

        scaling = [1, 1e3, 1e6, 1e9]

        if timespan > 0.0:
            order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
        else:
            order = 3
        return f"{timespan * scaling[order]:.{precision}g} {units[order]}"


class MagicCommandHandler:
    def __init__(self, shell):
        self.shell = shell
        self.command_handlers = {
            "%time": self.handle_time_command,
            "%timeit": self.handle_timeit_command,
            "%who": self.handle_who_command,
            "%whos": self.handle_whos_command,
        }

    def handle_magic_command(self, text):
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        handler = self.command_handlers.get(command, self.handle_unknown_command)
        handler(args)

    @staticmethod
    def handle_unknown_command(command):
        print(f"{color_print('SinglePython Warning:', 'magenta')} Unknown magic command: {command}")

    def handle_time_command(self, code_to_time):
        if not code_to_time:
            print(f"{color_print('SinglePython Warning:', 'magenta')} No code provided for %time")
            return

        self.execute_timed_code(code_to_time)

    def execute_timed_code(self, code_to_time=None):
        if code_to_time is None:
            code_to_time = "\n".join(self.shell.buffered_code)
            self.shell.buffered_code.clear()

        try:
            start_time = time.time()
            compiled_code = compile(code_to_time, "<input>", "exec")
            self.shell.interpreter.runcode(compiled_code)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"{color_print('Time taken:', 'cyan')} {self._format_time(execution_time)}")
        except Exception as e:
            self.shell.buffered_code.clear()
            self.shell.handle_exception(e, "Error")
            self.shell.increment_prompt()
        finally:
            self.shell.reset_state()

    def handle_timeit_command(self, code_to_time):
        if not code_to_time:
            print(f"{color_print('SinglePython Warning:', 'magenta')} No code provided for %timeit")
            return

        match = re.match(r"(-n\s+(\d+))?\s*(-r\s+(\d+))?\s*(.*)", code_to_time)
        if not match:
            print(
                f"{color_print('SinglePython Warning:', 'magenta')} Invalid syntax for %timeit. Use: %timeit [-n <number>] [-r <repeats>] <code>")
            return

        n = int(match.group(2)) if match.group(2) else 1000000
        r = int(match.group(4)) if match.group(4) else 7
        code_to_time = match.group(5).strip()

        self.execute_timeit_code(n, r, code_to_time)

    def execute_timeit_code(self, n, r, code_to_time=None):
        if code_to_time is None:
            code_to_time = "\n".join(self.shell.buffered_code)
            self.shell.buffered_code.clear()

        try:
            tqdm_file = open(sys.__stdout__.fileno(), mode='w', encoding='utf-8')

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                timer = Timer(stmt=code_to_time, globals=self.shell.interpreter.locals)
                times = []
                for _ in tqdm(range(r), desc="Timeit runs", unit="run", file=tqdm_file):
                    times.append(timer.timeit(number=n) / n)

                best = TimeFormatter.format_time(min(times))
                avg = TimeFormatter.format_time(sum(times) / len(times))
                worst = TimeFormatter.format_time(max(times))

            print(f"{color_print(f'Best of {r} runs, {n} loops each:', 'cyan')}")
            print(f"  Best: {best}  per loop")
            print(f"  Average: {avg}  per loop")
            print(f"  Worst: {worst}  per loop")

            tqdm_file.close()
        except Exception as e:
            self.shell.buffered_code.clear()
            self.shell.handle_exception(e, "Error")
            self.shell.increment_prompt()

    def handle_who_command(self, args):
        filtered_locals = {k: v for k, v in self.shell.interpreter.locals.items() if not k.startswith('__')}
        print(" , ".join(filtered_locals.keys()))

    def handle_whos_command(self, args):
        filtered_locals = {k: v for k, v in self.shell.interpreter.locals.items() if not k.startswith('__')}
        for key, value in filtered_locals.items():
            print(f"{key}: {value}")
