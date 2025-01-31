import os
import subprocess
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style as Style1
from pygments.lexers import PythonLexer

from Core.interpreter import MyInteractiveInterpreter
from Core.magic_commands import MagicCommandHandler
from Core.utils import color_print, show_startup_info

MULTILINE_KEYWORDS = {"if", "elif", "else", "for", "while", "def", "class"}

class SinglePythonShell:
    def __init__(self, version_info=None):
        self.version_info = version_info
        self.multiline_comment = False
        self.buffered_code = []
        self.input_count = 1
        self.session = self.init_prompt_session()
        self.prompt_message = f"In [{self.input_count}]: "
        self.interpreter = MyInteractiveInterpreter()
        self.first_line_processed = False
        self.magic_command_handler = MagicCommandHandler(self)

    def init_prompt_session(self):
        lexer = PygmentsLexer(PythonLexer)
        history = InMemoryHistory()
        style = Style1.from_dict({
            'pygments.keyword': 'bold #ff79c6',
            'pygments.operator': '#ff79c6',
            'pygments.punctuation': '#ff79c6',
            'pygments.name.function': '#50fa7b',
            'pygments.name.class': 'bold #50fa7b',
            'pygments.literal.string': '#f1fa8c',
            'pygments.literal.number': '#bd93f9',
            'pygments.comment': '#6272a4',
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
            CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
            subprocess.run(CLEAR_COMMAND, shell=True, check=False)
            self.reset_state()
            return True
        elif text.startswith("!"):
            subprocess.run(text[1:], shell=True, check=False)
            self.reset_state()
            return True
        elif text.startswith("%"):
            self.magic_command_handler.handle_magic_command(text)
            self.reset_state()
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
        elif text.strip() in self.interpreter.locals:
            print(f"Out[{self.input_count}]: {self.interpreter.locals[text.strip()]}\n")
            self.reset_state()
            return True
        self.buffered_code.append(text)
        if not self.first_line_processed:
            self.check_multiline_keywords(text)
            self.first_line_processed = True
        return False

    def run(self):
        if self.version_info:
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
