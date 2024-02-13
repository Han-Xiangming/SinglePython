SinglePythonInfo = {"version": 0.72,  # 版本号
                    "libs_warning": 1,  # 库警告
                    "releases_version": "official",  # 发布版本号
                    "importlibs": "os"  # 导入的库信息
                    }
import argparse
import ast
import builtins
import functools
import keyword
import os
import platform
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.completion import display_completions_like_readline
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer

# 颜色映射表
color_map = {'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m', 'magenta': '\033[95m',
             'cyan': '\033[96m', 'white': '\033[97m'}

# 设置适当的缓存大小，例如1000，如果缓存大小为None，则表示没有大小限制
color_print = functools.lru_cache(maxsize=1000)(lambda text, color: f"{color_map.get(color, '')}{text}\033[0m")


def get_version():
	"""
	获取当前版本号

	:返回: 当前版本号 (str)
	"""
	return f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}, By Python {platform.python_version()}"


class SinglePythonwin:
	"""
	SinglePythonwin 类用于设置控制台标题。

	使用方法：
	single_python = SinglePythonwin()
	single_python.set_console_title()
	"""

	def set_console_title(self):
		"""
		设置控制台标题为"SinglePython {version}"，使用ctypes库调用kernel32.dll中的SetConsoleTitleW函数。

		参数：
		- self: 类的实例。

		返回值：
		- 无
		"""

		import ctypes

		try:
			# 获取 SinglePython 的版本
			version = SinglePythonInfo['version']

			# 使用版本号设置控制台标题
			ctypes.windll.kernel32.SetConsoleTitleW(f"SinglePython {version}")
		except KeyError:
			print(f"{color_print('Error:', 'red')} SinglePythonInfo dictionary does not contain 'version' key.")
		except ctypes.WinError as e:
			print(f"{color_print('Error:', 'red')} Failed to set console title. Error: {e}")


# 生成包含所有内置函数和关键字的列表
def get_builtin_names_and_keywords():
	builtin_names = [name for name in dir(builtins) if not name.startswith("__")]
	keywords = list(keyword.kwlist)
	return builtin_names + keywords


completer = WordCompleter(get_builtin_names_and_keywords(), ignore_case=True)

# 缓存用户输入的代码片段
buffered_code = []


def optreadfile_exec(filename: str) -> None:
	"""
	在指定文件中运行 Python 代码

	:参数 filename： 字符串 包含 Python 代码的文件的名称 (str)
	:返回: None
	"""
	if not os.path.isfile(filename):
		# 如果指定文件不存在
		print(f"{color_print('SinglePython Error:', 'red')} File not found")
		return

	try:
		# 读取指定文件中的 Python 代码
		with open(filename, "r") as f:
			code = compile(f.read(), filename, 'exec')
		# 执行编译后的代码
		exec(code)
		print(" ")
		print(f"{color_print('SinglePython Info:', 'magenta')} {filename} executed successfully")
	except SyntaxError:
		# 如果存在语法错误
		print(f"{color_print('SyntaxError:', 'red')} Syntax error in the Python code")
	except Exception as e:
		# 如果存在其他异常
		print(f"{color_print('SinglePython Error:', 'red')}", str(e))


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
	sp_version = f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}"
	# 获取 Python 版本
	py_version = platform.python_version()
	# 获取运行环境信息
	env_info = f" [Running on {platform.platform()} {platform.version()}]"

	# 打印欢迎信息
	# 使用格式化字符串将 sp 版本、Python 版本和环境信息组合成欢迎信息
	welcome_message = f"{sp_version} (Python Version: {py_version}) {env_info}"
	# 将欢迎信息使用颜色设置为青色
	colored_message = color_print(welcome_message, 'cyan')
	# 打印带有颜色的欢迎信息
	print(colored_message)


def is_valid_python_code(code):
	"""
	检查给定的代码是否是有效的Python代码。

	:param code: 要检查的Python代码字符串
	:return: 如果代码是有效的Python代码则返回True，否则返回False
	"""
	try:
		return ast.parse(code, mode='eval').body is not None
	except SyntaxError as e:
		# 打印异常信息，有助于调试和错误追踪
		# print(f"SyntaxError: {e}")
		return False


def are_brackets_complete(code):
	"""
	检查给定的代码中的括号是否完整。

	:param code: 要检查的Python代码字符串
	:return: 如果所有括号都已正确闭合则返回True，否则返回False
	"""
	open_brackets = {'(', '[', '{'}
	close_brackets = {')', ']', '}'}
	bracket_map = {')': '(', ']': '[', '}': '{'}
	stack = []

	for char in code:
		if char in open_brackets:
			stack.append(char)
		elif char in close_brackets:
			if not stack or stack.pop() != bracket_map[char]:
				return False

	return not stack  # 如果栈为空，则所有括号都已正确闭合


def handle_tab(event):
	"""
	处理Tab键的按键事件。

	如果光标位置在文本的开头或者前一个字符是换行符或空格，插入四个空格。
	否则，调用display_completions_like_readline函数。

	:param event: 包含按键事件信息的对象
	"""
	# 确保event.app.current_buffer和buff.document.text是有效的引用
	buffer = event.app.current_buffer
	cursor_position = buffer.cursor_position
	document_text = buffer.document.text

	if cursor_position == 0 or (cursor_position > 0 and document_text[cursor_position - 1] in ('\n', ' ')):
		buffer.insert_text(' ' * 4)  # 假设每个缩进级别为4个空格
	else:
		# 确保display_completions_like_readline函数在当前上下文中是可用的
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


def main():
	parser = argparse.ArgumentParser(description='Interactive Python Shell with additional features.')
	parser.add_argument('-f', '--file', type=str, help='Execute Python code from the specified file')
	parser.add_argument('-i', '--interactive', action='store_true',
	                    help='Enter interactive mode after executing a file.')
	parser.add_argument('-v', '--version', action='version', version=get_version(), help='Show version information')
	args = parser.parse_args()
	if args.file:
		optreadfile_exec(args.file)
		if args.interactive:
			SinglePython_shell()
		else:
			sys.exit(0)
	else:
		SinglePython_shell()


def SinglePython_shell():
	"""
	创建一个交互式 Python 命令行界面。
	"""
	# 显示欢迎文本
	show_startup_info()
	# 创建一个PromptSession实例并配置历史记录、自动补全（包括WordCompleter）、语法高亮等
	lexer = PygmentsLexer(PythonLexer)
	history = InMemoryHistory()
	# 添加自定义按键绑定到PromptSession实例
	session = PromptSession(lexer=lexer, auto_suggest=AutoSuggestFromHistory(), completer=completer, history=history,
	                        key_bindings=bindings)
	# 初始提示符
	input_count = 1
	prompt_message = f"In [{input_count}]: "
	while True:
		try:
			# 获取用户输入
			text = session.prompt(prompt_message)
			if text == 'exit':
				sys.exit(0)
			elif text == 'cls' or text == 'clear':
				# 清屏
				os.system('cls' if os.name == 'nt' else 'clear')
				input_count += 1
				prompt_message = f"In [{input_count}]: "
				continue
			elif text.startswith("!"):
				# 执行系统命令
				os.system(text[1:])
				input_count += 1
				prompt_message = f"In [{input_count}]: "
				continue
			elif text.endswith("?"):
				# 输出变量信息
				variable_name = text[:-1]
				if variable_name in globals() or variable_name in locals():
					variable_value = eval(variable_name)
					print(f"{color_print('Name:', 'red')}  {variable_name}")
					print(f"{color_print('Type: ', 'red')} {type(variable_value).__name__}")
					print(f"{color_print('Value:', 'red')} {variable_value}")
					print(f"{color_print('Size:', 'red')}  {sys.getsizeof(variable_value)} bytes")
					print(f"{color_print('Description:', 'red')} {variable_value.__doc__}")
					print("\n")
				else:
					print(f"{color_print('SinglePython Error:', 'red')} Variable not found")
				input_count += 1
				prompt_message = f"In [{input_count}]: "
				continue
			# 输出变量值
			elif text in globals() or text in locals():
				print(f"{color_print(f'Out[{input_count}]:', 'blue')} {eval(text)}")
				input_count += 1
				prompt_message = f"In [{input_count}]: "
				continue
			elif '.py' in text[-4:]:
				text = str(text).replace('"', '')
				optreadfile_exec(text)
				input_count += 1
				prompt_message = f"In [{input_count}]: "
				continue
			# 添加代码到缓冲区
			buffered_code.append(text)
			# 检查代码是否完整
			if (is_valid_python_code(''.join(buffered_code)) and are_brackets_complete(
					''.join(buffered_code))) or text == '' or 'import' in text:
				# 执行代码并重置提示符和缓冲区
				input_count += 1
				prompt_message = f"In [{input_count}]: "
				try:
					exec('\n'.join(buffered_code))
					# print(f"Executed code: {'\n'.join(buffered_code)}")
					buffered_code.clear()
					print(' ')
				except Exception as e:
					buffered_code.clear()
					print(str(e))
					print(' ')
					continue
			else:
				prompt_message = '   ...:'

		except KeyboardInterrupt:
			# 中止执行
			buffered_code.clear()
			print("\nKeyboardInterrupt")
			print(' ')
			input_count += 1
			prompt_message = f"In [{input_count}]: "
			continue
		except EOFError:
			# 文件结束
			print("\nExiting...")
			break


if __name__ == '__main__':
	main()
