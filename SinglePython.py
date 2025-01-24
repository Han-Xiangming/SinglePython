import code
import os
import platform
import subprocess
import sys
import traceback
from argparse import ArgumentParser
from time import time

from colorama import Fore, Style, init
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style as Style1
from pygments.lexers import PythonLexer

# 初始化 colorama
init()

# 常量定义
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
IMPORT_CHECK = "import"
EMPTY_LINE = ""
MULTILINE_KEYWORDS = {"if", "elif", "else", "for", "while", "def", "class"}  # 使用集合提高查找效率

# 配置信息
SinglePythonInfo = {
    "version": 0.88,
    "libs_warning": 1,
    "releases_version": "official",
    "importlibs": "os",
}

# 缓存版本信息
_cached_version = None


def get_version():
    global _cached_version
    if _cached_version is None:
        _cached_version = f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}, By Python {platform.python_version()}"
    return _cached_version


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


def execute_code(code_content, filename):
    try:
        if not code_content.strip():
            print(f"{color_print('SinglePython Warning:', 'magenta')} {filename} is empty")
            return
        codes = compile(code_content, filename, "exec")
        exec(codes)
        print(f"{color_print('SinglePython Info:', 'magenta')} {filename} executed successfully")
    except Exception as e:
        handle_exception(e, "SinglePython Error")


def optreadfile_exec(filename: str) -> None:
    try:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File {filename} not found")
        with open(filename, "r", encoding="utf-8") as f:
            code_content = f.read()
        execute_code(code_content, filename)
    except Exception as e:
        handle_exception(e, "SinglePython Error")


class MyInteractiveInterpreter(code.InteractiveInterpreter):
    def __init__(self):
        super().__init__()
        self.buffer = []

    def runsource(self, source, filename="<input>", symbol="exec"):
        self.buffer.append(source)
        source = "\n".join(self.buffer)
        if code.compile_command(source) is not None:
            self.buffer = []
            return super().runsource(source, filename, symbol)
        return True


class MagicCommandHandler:
    def __init__(self, shell):
        self.shell = shell

    def handle_magic_command(self, text):
        command, *args = text.split(maxsplit=1)
        if command == "%time":
            self.handle_time_command(args[0] if args else "")
        else:
            print(f"{color_print('SinglePython Warning:', 'magenta')} Unknown magic command: {command}")

    def handle_time_command(self, code_to_time):
        if not code_to_time:
            print(f"{color_print('SinglePython Warning:', 'magenta')} No code provided for %time")
            return

        if self.shell.multiline_comment:
            self.shell.buffered_code.append(code_to_time)
            if self.shell.check_multiline_end():
                self.execute_timed_code()
        else:
            self.execute_timed_code(code_to_time)

    def execute_timed_code(self, code_to_time=None):
        if code_to_time is None:
            code_to_time = "\n".join(self.shell.buffered_code)
            self.shell.buffered_code.clear()

        try:
            start_time = time()
            compiled_code = compile(code_to_time, "<input>", "exec")
            self.shell.interpreter.runcode(compiled_code)
            end_time = time()
            execution_time = end_time - start_time
            print(f"{color_print('Time taken:', 'cyan')} {execution_time:.6f} seconds")
        except Exception as e:
            self.shell.buffered_code.clear()
            self.shell.handle_exception(e, "Error")
            self.shell.increment_prompt()
        finally:
            self.shell.reset_state()


class SinglePythonShell:
    def __init__(self, version_info):
        self.multiline_comment = False
        self.buffered_code = []
        self.input_count = 1
        self.version_info = version_info
        self.session = self.init_prompt_session()
        self.prompt_message = f"In [{self.input_count}]: "
        self.interpreter = MyInteractiveInterpreter()
        self.first_line_processed = False
        self.magic_command_handler = MagicCommandHandler(self)

    def init_prompt_session(self):
        lexer = PygmentsLexer(PythonLexer)
        history = InMemoryHistory()
        style = Style1.from_dict({
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
            'scrollbar.background': 'bg:#88aaaa',
            'scrollbar.button': 'bg:#222222',
        })
        return PromptSession(
            lexer=lexer,
            auto_suggest=AutoSuggestFromHistory(),
            history=history,
            key_bindings=self.get_key_bindings(),
            style=style,
        )

    @staticmethod
    def get_key_bindings():
        bindings = KeyBindings()

        @bindings.add(Keys.Tab)
        def handle_tab(event):
            buffer = event.app.current_buffer
            buffer.insert_text(" " * 4)

        @bindings.add("c-c")
        def handle_ctrl_c(event):
            print("\nExiting gracefully on Ctrl+C...")
            sys.exit(0)

        return bindings

    def increment_prompt(self):
        self.input_count += 1
        self.prompt_message = f"In [{self.input_count}]: "

    def check_multiline_keywords(self, codes):
        stripped_code = codes.strip()
        if stripped_code == "":
            self.multiline_comment = False
            return False
        if stripped_code.endswith(":"):
            for kw in MULTILINE_KEYWORDS:
                if stripped_code.startswith(kw):
                    self.multiline_comment = True
                    return True
        self.multiline_comment = False
        return False

    def reset_state(self):
        self.buffered_code.clear()
        self.increment_prompt()
        self.multiline_comment = False
        self.first_line_processed = False

    def handle_exception(self, e, message_prefix):
        print(f"{color_print(f'{message_prefix}:', 'red')} {e}")
        self.reset_state()

    def handle_user_input(self, text):
        if text == "exit":
            sys.exit(0)
        elif text in ["cls", "clear"]:
            subprocess.call(CLEAR_COMMAND, shell=True)
            self.reset_state()
            return True
        elif text.startswith("!"):
            subprocess.call(text[1:], shell=True)
            self.reset_state()
            return True
        elif text.startswith("%"):
            self.magic_command_handler.handle_magic_command(text)
            return True
        elif text.strip() == "":
            if self.multiline_comment:
                try:
                    compiled_code = compile("\n".join(self.buffered_code), "<input>", "exec")
                    self.interpreter.runcode(compiled_code)
                    self.reset_state()
                except Exception as e:
                    self.handle_exception(e, "Error")
                return True
        self.buffered_code.append(text)
        if not self.first_line_processed:
            self.check_multiline_keywords(text)
            self.first_line_processed = True
        return False

    def run(self):
        show_startup_info(self.version_info)
        while True:
            try:
                prompt_message = "   ...:" if self.multiline_comment else self.prompt_message
                text = self.session.prompt(prompt_message)
                if self.handle_user_input(text):
                    continue

                if not self.multiline_comment:
                    try:
                        compiled_code = compile("\n".join(self.buffered_code), "<input>", "exec")
                        self.interpreter.runcode(compiled_code)
                        self.reset_state()
                    except Exception as e:
                        self.buffered_code.clear()
                        self.handle_exception(e, "Error")
                        self.increment_prompt()
                        continue

            except KeyboardInterrupt:
                self.buffered_code.clear()
                print("\nKeyboardInterrupt")
                self.reset_state()
                continue
            except EOFError:
                print("\nExiting...")
                break


def main():
    parser = ArgumentParser(description="Interactive Python Shell with additional features.")
    parser.add_argument("-f", "--file", type=str, help="Execute Python code from the specified file")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after executing a file.")
    parser.add_argument("-v", "--version", action="version", version=get_version(), help="Show version information")
    args = parser.parse_args()

    try:
        if args.file:
            optreadfile_exec(args.file)
            if args.interactive:
                shell = SinglePythonShell(SinglePythonInfo)
                shell.run()
            else:
                sys.exit(0)
        else:
            shell = SinglePythonShell(SinglePythonInfo)
            shell.run()
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
