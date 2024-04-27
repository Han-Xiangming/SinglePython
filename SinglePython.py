import builtins
import ctypes
import keyword
import os
import platform
import sys
import traceback
from argparse import ArgumentParser

from colorama import Fore, Style, init
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.completion import display_completions_like_readline
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style as Style1
from pygments.lexers import PythonLexer

# 常量定义
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
IMPORT_CHECK = "import"
EMPTY_LINE = ""

SinglePythonInfo = {
    "version": 0.81,  # 版本号
    "libs_warning": 1,  # 库警告
    "releases_version": "official",  # 发布版本号
    "importlibs": "os",  # 导入的库信息
}

# 初始化 colorama
init()


def color_print(text, color):
    """
        根据给定的颜色，将文本以指定颜色输出。

        参数：
        text (str): 需要输出的文本。
        color (str): 颜色名称，可选值为 "red"、"green"、"yellow"、"blue"、"magenta"、"cyan"、"white"。

        返回：
        str: 指定颜色的文本。

        """

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


def get_version():
    """
        获取当前版本号

        :返回: 当前版本号 (str)
        """
    return f"SinglePython {
    SinglePythonInfo['version']}-{
    SinglePythonInfo['releases_version']}, By Python {
    platform.python_version()}"


class SinglePythonwin:
    """
    SinglePythonwin 类用于设置控制台标题。
    """

    @staticmethod
    def set_console_title():
        """
        设置控制台标题为"SinglePython {version}"，使用ctypes库调用kernel32.dll中的SetConsoleTitleW函数。

        参数：
        - self: 类的实例。

        返回值：
        - 无
        """
        try:
            version = SinglePythonInfo["version"]
            ctypes.windll.kernel32.SetConsoleTitleW(f"SinglePython {version}")
        except KeyError:
            print(f"{color_print('Error:', 'red')} SinglePythonInfo dictionary does not contain 'version' key.")
        except ctypes.WinError as e:
            print(f"{color_print('Error:', 'red')} Failed to set console title. Error: {e}")


# 生成包含所有内置函数和关键字的列表
def get_builtin_names_and_keywords():
    """
    获取所有内置函数和关键字的名称，并将它们合并到一个列表中返回。

    :return: 包含所有内置函数名称和关键字的列表
    """
    try:
        # 获取所有内置函数名称
        builtin_names = [name for name in dir(builtins) if not name.startswith("__")]

        # 获取所有关键字
        keywords = list(keyword.kwlist)

        # 返回内置函数和关键字的列表
        return builtin_names + keywords
    except Exception as e:
        # 在发生异常时打印错误信息并返回空列表
        # 实际应用中，可能需要更复杂的错误处理逻辑
        print(color_print(f"获取内置名称和关键字时发生错误: {e}", "red"))
        return []


# 创建一个词补全器对象
completer = WordCompleter(get_builtin_names_and_keywords(), ignore_case=True)

# 缓存用户输入的代码片段
buffered_code = []


def optreadfile_exec(filename: str) -> None:
    """
        在指定文件中运行 Python 代码

        :参数 filename： 字符串 包含 Python 代码的文件的名称 (str)
        :返回: None
        """
    try:
        # 打开文件并读取内容
        with open(filename, "r") as f:
            code = compile(f.read(), filename, "exec")
        # 执行代码
        exec(code)
        print(" ")
        print(f"{color_print('SinglePython Info:', 'magenta')} {
        filename} executed successfully")
    except FileNotFoundError:
        # 文件未找到
        print(f"{color_print('SinglePython Error:', 'red')} File not found")
    except SyntaxError:
        # 语法错误
        print(f"{color_print('SyntaxError:', 'red')
        } Syntax error in the Python code")
    except Exception as e:
        # 其他异常
        print(f"{color_print('SinglePython Error:', 'red')}", e)


def show_startup_info():
    """
        打印程序的启动信息。

        - 从 'SinglePythonInfo' 字典中获取 SinglePython 版本。
        - 使用 'platform.python_version()' 函数获取 Python 版本。
        - 使用 'platform.platform()' 和 'platform.version()' 函数获取运行环境信息。
        - 将 SinglePython 版本、Python 版本和环境信息组合成欢迎信息。
        - 使用 'color_print' 函数将欢迎信息的颜色设置为青色。
        - 打印带有颜色的欢迎信息。

        参数：
        无

        返回值：
        无
        """
    # 获取 SinglePython 版本
    sp_version = f"SinglePython {
    SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}"
    # 获取 Python 版本
    py_version = platform.python_version()
    # 获取运行环境信息
    env_info = f" [Running on {platform.platform()} {platform.version()}]"

    # 打印欢迎信息
    # 使用格式化字符串将 sp 版本、Python 版本和环境信息组合成欢迎信息
    welcome_message = f"{sp_version} (Python Version: {py_version}) {env_info}"

    # 打印带有颜色的欢迎信息
    print(color_print(welcome_message, "cyan"))


def handle_tab(event):
    """
        处理Tab键的按键事件。

        如果光标位置在文本的开头或者前一个字符是换行符或空格，插入四个空格。
        否则，调用display_completions_like_readline函数。

        :param event: 包含按键事件信息的对象
        """
    buffer = event.app.current_buffer
    if buffer.cursor_position == 0 or buffer.document.text[buffer.cursor_position - 1] in (
            "\n", " "):
        buffer.insert_text(" " * 4)
    else:
        display_completions_like_readline(event)


# 添加自定义按键绑定
bindings = KeyBindings()


# 当用户按下Tab键时，调用handle_tab函数处理事件
@bindings.add(Keys.Tab)
def handle_tab_key(event):
    """
        处理Tab键的事件。

        :param event: 事件对象，包含按键信息
        """
    handle_tab(event)


# 添加Ctrl+C退出功能
@bindings.add("c-c")
def handle_ctrl_c():
    """
    处理Ctrl+C按键事件，优雅地退出程序。

    参数:
    - event: 触发此函数的事件对象，具体类型和属性取决于事件绑定库。

    返回值:
    - 无
    """
    print("\nExiting gracefully on Ctrl+C...")
    sys.exit(0)


def increment_prompt(input_count):
    """
        对输入的计数进行加一操作，并返回更新后的计数和提示信息。
        """
    input_count += 1  # 将输入的计数值增加1
    prompt_message = f"In [{input_count}]: "  # 根据更新后的计数值生成提示信息
    return input_count, prompt_message  # 返回更新后的计数和提示信息


# 写一个函数判断传入的代码文本中是否含有需要进入多行输入模式的关键词
def check_multiline_keywords(code):
    """
    检查给定的代码中是否包含需要进入多行输入模式的关键词。

    :param code: 要检查的Python代码字符串
    :return: 如果包含需要进入多行输入模式的关键词则返回True，否则返回False
    """
    if code == "":
        return False
    # try:
    #     parsed = ast.parse(code)
    # except SyntaxError:
    #     return False
    multiline_keywords = ["if", "elif", "else", "for", "while", "def", "class"]
    for c_keyword in multiline_keywords:
        if code.startswith(c_keyword) and code.endswith(":"):
            return True
    return False


def main():
    """
        执行主程序。

        创建一个ArgumentParser对象并添加命令行参数。
        解析命令行参数并执行指定文件中的Python代码或进入交互模式。

        """
    # 创建ArgumentParser对象
    parser = ArgumentParser(
        description="Interactive Python Shell with additional features.")
    # 添加命令行参数
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Execute Python code from the specified file")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after executing a file.")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version(),
        help="Show version information")
    # 解析命令行参数
    args = parser.parse_args()
    try:
        # 如果指定了文件参数
        if args.file:
            # 执行指定文件中的Python代码
            optreadfile_exec(args.file)
            # 如果指定了交互模式参数
            if args.interactive:
                # 进入交互模式
                SinglePython_shell()
            else:
                # 退出程序
                sys.exit(0)
        else:
            # 进入交互模式
            SinglePython_shell()
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred: {e}")
        sys.exit(1)


def SinglePython_shell():
    """
        创建一个交互式 Python 命令行界面。

        显示欢迎文本并创建一个PromptSession实例，配置历史记录、自动补全、语法高亮等。
        处理用户输入，执行系统命令、输出变量信息、执行Python代码等。

        """
    ...

    # 显示欢迎文本
    show_startup_info()
    # 创建一个PromptSession实例并配置历史记录、自动补全（包括WordCompleter）、语法高亮等
    lexer = PygmentsLexer(PythonLexer)
    history = InMemoryHistory()
    style12 = Style1.from_dict({
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })
    # 添加自定义按键绑定到PromptSession实例
    session = PromptSession(
        lexer=lexer,
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        history=history,
        key_bindings=bindings,
        style=style12,
        complete_while_typing=True,
        complete_in_thread=True,
    )
    # 初始提示符
    input_count = 1
    prompt_message = f"In [{input_count}]: "
    while True:
        try:
            # 获取用户输入
            text = session.prompt(prompt_message)
            if text == "exit":
                sys.exit(0)
            elif text in ["cls", "clear"]:
                # 清屏
                os.system(CLEAR_COMMAND)
                input_count, prompt_message = increment_prompt(input_count)
                continue
            elif text.startswith("!"):
                # 执行系统命令
                os.system(text[1:])
                input_count, prompt_message = increment_prompt(input_count)
                continue
            elif text.endswith("?"):
                # 输出变量信息
                variable_name = text[:-1]
                if variable_name in globals() or variable_name in locals():
                    variable_value = eval(variable_name)
                    print(f"{color_print('Name:', 'red')}  {variable_name}")
                    print(f"{color_print('Type: ', 'red')} {
                    type(variable_value).__name__}")
                    print(f"{color_print('Value:', 'red')} {variable_value}")
                    print(f"{color_print('Size:', 'red')}  {
                    sys.getsizeof(variable_value)} bytes")
                    print(f"{color_print('Description:', 'red')} {
                    variable_value.__doc__}")
                    print("\n")
                else:
                    print(f"{color_print('SinglePython Error:', 'red')
                    } Variable not found")
                input_count, prompt_message = increment_prompt(input_count)
                continue
            elif text in globals() or text in locals():
                print(f"{color_print(f'Out[{input_count}]:', 'blue')} {
                eval(text)}")
                input_count, prompt_message = increment_prompt(input_count)
                continue
            elif ".py" in text[-4:]:
                text = str(text).replace('"', "")
                optreadfile_exec(text)
                input_count, prompt_message = increment_prompt(input_count)
                continue

            # 添加代码到缓冲区
            buffered_code.append(text)
            if check_multiline_keywords(buffered_code[-1]):
                prompt_message = "   ...:"
            else:
                input_count, prompt_message = increment_prompt(input_count)
                try:
                    exec("\n".join(buffered_code))
                    # print(f"Executed code: {'\n'.join(buffered_code)}")
                    buffered_code.clear()
                except Exception as e:
                    buffered_code.clear()
                    print(color_print(e, 'red'))
                    continue

        except KeyboardInterrupt:
            # 中止执行
            buffered_code.clear()
            print("\nKeyboardInterrupt")
            input_count, prompt_message = increment_prompt(input_count)
            continue
        except EOFError:
            # 文件结束
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
