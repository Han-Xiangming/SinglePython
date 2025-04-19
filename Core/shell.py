# shell.py

import contextlib
import sys
import os
import subprocess
import re

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.history import History

class BlockAutoSuggestFromHistory(AutoSuggest):
    """
    基于历史记录的多行补全：每次建议以完整历史块为单位。
    """
    def get_suggestion(self, buffer, document):
        history: History = buffer.history
        text = document.text
        if not text.strip():
            return None
        # 倒序查找历史，找到以当前输入开头的完整历史块
        for entry in reversed(list(history.get_strings())):
            entry = entry.rstrip("\n")
            if entry.startswith(text) and entry != text:
                if suggestion := entry[len(text) :]:
                    return Suggestion(suggestion)
        return None

from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers import PythonLexer

from Core.interpreter import MyInteractiveInterpreter
from Core.magic_commands import MagicCommandHandler
from Core.utils import color_print, show_startup_info

MULTILINE_KEYWORDS = {"if", "elif", "else", "for", "while", "def", "class"}
DEDENT_KEYWORDS = {"elif", "else", "except", "finally"}

PROMPT_STYLE = Style.from_dict({
    'pygments.keyword': 'bold #ff79c6',
    'pygments.operator': '#ff79c6',
    'pygments.punctuation': '#ff79c6',
    'pygments.name.function': '#50fa7b',
    'pygments.name.class': 'bold #50fa7b',
    'pygments.literal.string': '#f1fa8c',
    'pygments.literal.number': '#bd93f9',
    'pygments.comment': '#6272a4',
})


class SinglePythonShell:
    """
    交互式 Python Shell，支持多行输入、魔法命令、语法高亮等功能。
    """

    CURSOR_NONE = 0   # 无
    CURSOR_LINE = 1   # 线
    CURSOR_BLOCK = 2   # 方块
    CURSOR_CIRCLE = 3 # 圆
    CURSOR_UNDERLINE = 4  # 下划线
    CURSOR_BLINKING_LINE = 5  # 闪烁线
    CURSOR_BAR = 6    # 条形

    @staticmethod
    def set_cursor_shape(shape: int):
        # shape: 0=无, 1=线, 2=方块,3=圆, 4=下划线, 5=闪烁线, 6=条形
        with contextlib.suppress(Exception):
            sys.stdout.write(f"\033[{shape} q")
            sys.stdout.flush()

    def __init__(self, version_info=None):
        self.version_info = version_info
        self.multiline_comment = False
        self.buffered_code = []
        self._indent_stack = [0]  # 用于缓存缩进层级
        self.input_count = 1
        self.session = self.init_prompt_session()
        self.prompt_message = f"In [{self.input_count}]: "
        self.interpreter = MyInteractiveInterpreter()
        self.first_line_processed = False
        self.magic_command_handler = MagicCommandHandler(self)

    def init_prompt_session(self):
        """
        初始化 prompt_toolkit 的会话，包括高亮、历史、样式和快捷键绑定。
        """
        lexer = PygmentsLexer(PythonLexer)
        self._history = InMemoryHistory()  # 持有 history 实例，便于后续操作
        return PromptSession(
            lexer=lexer,
            auto_suggest=BlockAutoSuggestFromHistory(),
            history=self._history,
            key_bindings=self.get_key_bindings(),
            style=PROMPT_STYLE,
            enable_history_search=True,
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

        @bindings.add("(")
        def handle_left_parenthesis(event):
            buffer = event.app.current_buffer
            buffer.insert_text("()")
            buffer.cursor_left()

        @bindings.add("[")
        def handle_left_bracket(event):
            buffer = event.app.current_buffer
            buffer.insert_text("[]")
            buffer.cursor_left()

        @bindings.add("{")
        def handle_left_brace(event):
            buffer = event.app.current_buffer
            buffer.insert_text("{}")
            buffer.cursor_left()

        return bindings

    def increment_prompt(self):
        self.input_count += 1
        self.prompt_message = f"In [{self.input_count}]: "

    def check_multiline_keywords(self, codes):
        stripped_code = codes.strip()
        if not stripped_code:
            self.multiline_comment = False
            return False
        if stripped_code.endswith(":"):
            first_word = stripped_code.split()[0] if stripped_code.split() else ""
            if first_word in MULTILINE_KEYWORDS:
                self.multiline_comment = True
                return True
        self.multiline_comment = False
        return False

    def reset_state(self):
        self.buffered_code.clear()
        self._indent_stack = [0]
        self.increment_prompt()
        self.multiline_comment = False
        self.first_line_processed = False

    def handle_exception(self, e, message_prefix):
        print(f"{color_print(f'{message_prefix}:', 'red')} {e}")
        self.reset_state()

    def _update_indent_stack(self, text):
        """
        增量维护缩进栈，仅在有新行加入时更新。
        """
        INDENT = '    '
        stack = self._indent_stack.copy() if self._indent_stack else [0]
        stripped = text.strip()
        if not stripped or stripped.startswith('#'):
            self._indent_stack = stack
            return
        if any(stripped.startswith(kw) for kw in DEDENT_KEYWORDS) and stripped.endswith(':'):
            if len(stack) > 1:
                stack.pop()
            stack.append(stack[-1] + len(INDENT))
        elif stripped.endswith(':'):
            stack.append(stack[-1] + len(INDENT))
        self._indent_stack = stack

    def handle_user_input(self, text):
        stripped_text = text.strip()
        if stripped_text == "exit":
            sys.exit(0)
        elif stripped_text in {"cls", "clear"}:
            CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
            subprocess.run(CLEAR_COMMAND, shell=True, check=False)
            self.reset_state()
            return True
        elif stripped_text.startswith("!"):
            subprocess.run(stripped_text[1:], shell=True, check=False)
            self.reset_state()
            return True
        elif stripped_text.startswith("%"):
            self.magic_command_handler.handle_magic_command(text)
            self.reset_state()
            return True
        elif not stripped_text:
            if self.multiline_comment:
                try:
                    compiled_code = compile("\n".join(self.buffered_code), "<input>", "exec")
                    self.interpreter.runcode(compiled_code)
                    self.reset_state()
                except Exception as e:
                    self.handle_exception(e, "Error")
                return True
        elif stripped_text in self.interpreter.locals:
            print(f"Out[{self.input_count}]: {self.interpreter.locals[stripped_text]}\n")
            self.reset_state()
            return True
        self._update_indent_stack(text)
        self.buffered_code.append(text)
        if not self.first_line_processed:
            self.check_multiline_keywords(text)
            self.first_line_processed = True
        return False


    def get_next_indent(self):
        """
        结合缩进栈与上一行判断，支持多层嵌套、dedent、块首自动缩进。
        利用 _indent_stack 缓存提升效率。
        """
        if not self.buffered_code:
            return ''
        last_stripped = self.buffered_code[-1].strip()
        if any(last_stripped.startswith(kw) for kw in DEDENT_KEYWORDS) and last_stripped.endswith(':'):
            return ' ' * self._indent_stack[-1]
        elif last_stripped.endswith(':'):
            return ' ' * self._indent_stack[-1]
        else:
            return ' ' * (self._indent_stack[-1] if self._indent_stack else 0)
    
    def run(self):
        if self.version_info:
            show_startup_info(self.version_info)
        try:
            while True:
                try:
                    # 输入前设置为闪烁线光标
                    self.set_cursor_shape(self.CURSOR_BLINKING_LINE)
                    prompt_message = "   ...:" if self.multiline_comment else self.prompt_message
                    # 多层嵌套自动缩进
                    default_indent = self.get_next_indent()
                    text = self.session.prompt(prompt_message, default=default_indent)
                    # 输入后恢复为方块光标
                    self.set_cursor_shape(self.CURSOR_BLOCK)

                    # 优化历史记录：多行输入合并为一个历史项，避免重复
                    def add_history_entry(code_block):
                        if code_block and hasattr(self, '_history'):
                            history_strings = list(self._history.get_strings())
                            if not history_strings or history_strings[-1] != code_block:
                                self._history.append_string(code_block)

                    # 支持粘贴多行代码：如果输入包含换行符，逐行处理并自动缩进
                    if "\n" in text:
                        lines = text.splitlines()
                        handled = False
                        for idx, line in enumerate(lines):
                            # 粘贴时自动缩进：上一行结尾冒号则补4空格
                            if idx > 0 and lines[idx-1].rstrip().endswith(":") and not line.startswith("    "):
                                line = f"    {line}"
                            if self.handle_user_input(line):
                                handled = True
                                break
                        if handled:
                            # 粘贴多行时合并历史
                            add_history_entry("\n".join(lines))
                            continue
                    else:
                        if self.handle_user_input(text):
                            # 单行输入直接写入历史
                            add_history_entry(text)
                            continue

                    if not self.multiline_comment:
                        try:
                            compiled_code = compile("\n".join(self.buffered_code), "<input>", "exec")
                            self.interpreter.runcode(compiled_code)
                            # 多行模式结束，合并历史
                            add_history_entry("\n".join(self.buffered_code))
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
        finally:
            # 程序退出时恢复为方块光标
            self.set_cursor_shape(self.CURSOR_BLOCK)

