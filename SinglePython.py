SinglePythonInfo = {"version": 0.61,  # 版本号
                    "libs_warning": 1,  # 库警告
                    "releases_version": "official",  # 发布版本号
                    "importlibs": "os"  # 导入的库信息
                    }


def color_print(text: str, color: str) -> str:
	"""
	以指定颜色打印文本。

	:参数 text: 要打印的文本。
	:参数 color: 文本的颜色，以字符串形式表示。
	"""
	colors: Dict[str, str] = {'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m',
	                          'magenta': '\033[95m', 'cyan': '\033[96m', 'white': '\033[97m'}

	return colors.get(color, '') + text + '\033[0m'


try:
	from getopt import getopt, GetoptError  # 导入 getopt 和 GetoptError 模块
	import sys  # 导入 sys 模块
	import platform  # 导入 platform 模块
	import os  # 导入 os 模块
	from typing import Dict  # 导入 Dict 类型
	from pathlib import Path  # 导入 Path 类型
	from collections import deque  # 导入 deque 类型
except ImportError:
	# 捕获导入错误异常，如果导入模块失败，则打印错误信息并退出程序
	print(f"{color_print('SinglePython Error:', 'red')} Import Error")
	sys.exit()
except Exception as e:
	# 捕获其他异常，如果出现其他错误，则打印错误信息并退出程序
	print(f"{color_print('SinglePython Error:', 'red')} {str(e)}")
	sys.exit()

history_list = deque()  # 创建一个空列表，用于存储历史记录


class SinglePythonwin:
	def set_console_title(self):
		"""
		设置控制台标题为"SinglePython {version}"，使用ctypes库调用kernel32.dll中的SetConsoleTitleW函数。

		参数：
		- self: 类的实例。

		返回值：
		- 无
		"""

		import ctypes

		# 获取 SinglePython 的版本
		version = SinglePythonInfo['version']

		# 使用版本号设置控制台标题
		ctypes.windll.kernel32.SetConsoleTitleW(f"SinglePython {version}")


# 定义 optreadfile_exec 函数，用于运行指定文件中的 Python 代码
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


# 定义 show_startup_info 函数，用于显示欢迎信息
def show_startup_info():
	# 获取 SinglePython 版本
	sp_version = f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}"
	# 获取 Python 版本
	py_version = platform.python_version()
	# 获取运行环境信息
	env_info = f" [Running on {platform.platform()} {platform.version()}]"

	# 打印欢迎信息
	# 使用格式化字符串将 sp 版本、Python 版本和环境信息组合成欢迎信息
	welcome_message = f"{sp_version} (Python 版本: {py_version}) {env_info}"
	# 将欢迎信息使用颜色设置为青色
	colored_message = color_print(welcome_message, 'cyan')
	# 打印带有颜色的欢迎信息
	print(colored_message)


# 定义 SinglePython_shell 函数，提供交互式 Python 解释器
def SinglePython_shell():
	input_count = 1  # 设置输入计数为1
	# 循环接收用户输入并执行
	while True:
		try:
			# 初始化多行输入标志
			multiline_input = False
			input_buffer = ""

			# 循环读取用户输入
			while True:
				# 根据 multiline_input 设置提示符号
				prompt = "   ...:" if multiline_input else f"In [{input_count}]: "
				# 读取一行用户输入
				user_input = input(prompt)
				# 添加到缓冲区
				input_buffer += user_input + "\n"
				# 判断用户输入
				# 如果用户输入为空字符串，结束多行输入
				if user_input.strip() == "":
					multiline_input = False
				# 如果用户输入以 ":" 结束，表示多行输入
				elif user_input.strip().endswith(":"):
					multiline_input = True
				# 否则，表示单行输入
				else:
					multiline_input = False
				input_count += 1  # 输入计数加一
				history_list.append(user_input)  # 将用户输入添加到历史记录列表中

				if user_input == "exit":
					# 如果用户输入为 "exit"，结束程序
					sys.exit()
				elif user_input.startswith("!"):
					# 如果用户输入以 "!" 开头，则执行系统命令
					os.system(user_input[1:])
					break
				elif user_input.endswith("?"):
					# 如果用户输入以 "?" 结尾，则尝试输出以"?"前的值为变量名的数据类型、值等信息
					variable_name = user_input[:-1]
					if variable_name in globals() or variable_name in locals():
						variable_value = eval(variable_name)
						print(f"{color_print('Name:', 'red')}  {variable_name}")
						print(f"{color_print('Type: ', 'red')} {type(variable_value).__name__}")
						print(f"{color_print('Value:', 'red')} {variable_value}")
						print(f"{color_print('Size:', 'red')}  {sys.getsizeof(variable_value)} bytes")
						print(f"{color_print('Description:', 'red')} {variable_value.__doc__}")

					else:
						print(f"{color_print('SinglePython Error:', 'red')} Variable not found")
					break

				# 如果用户输入的为已定义的变量名，则尝试输出该变量的值。
				elif user_input in globals() or user_input in locals():
					# 使用eval函数对变量名进行求值，并输出值
					print(f"{color_print(f'Out[{input_count - 1}]:', 'blue')} {eval(user_input)}")
				# 如果用户输入为 "cls" 或 "clear"，清屏并重置欢迎信息
				elif user_input in ('cls', 'clear'):
					"""
					如果用户输入为'cls'或'clear'
					根据操作系统类型执行不同的命令
					'cls'用于Windows操作系统，'clear'用于其他操作系统
					"""
					os.system('cls' if os.name == 'nt' else 'clear')
					# 调用show_startup_info函数显示启动信息
					show_startup_info()
					input_count = 1
					break

				# 如果用户输入中含有 ".py"，尝试执行指定的文件
				elif '.py' in user_input:
					user_input = str(user_input).replace('"', '')
					optreadfile_exec(user_input)
					break
				# 如果用户输入为 "history"，打印历史记录
				elif user_input == "history":
					history_list.remove("history")
					# 打印历史记录
					if len(history_list) == 0:
						print(color_print("No history", 'red'))
						break
					else:
						# 打印历史记录的索引和内容
						for i, item in enumerate(history_list):
							print(f"{color_print(f"{i + 1} ", 'blue')} {item}")
						break
				# 如果用户输入为 "clear_history"，清空历史记录
				elif user_input == "clear_history":
					clear_history = lambda: history_list.clear()
					# 调用clear_history函数清空历史记录
					clear_history()
					break
				# 如果不是多行输入，则尝试执行缓冲区内的代码
				if not multiline_input:
					try:
						exec(input_buffer)
						# 清空缓冲区
						input_buffer = ""
					except Exception as e:
						# 执行时遇到异常，打印错误信息并继续读取下一条命令
						print(f"{color_print('Error:', 'red')} {e}")
						input_buffer = ""
		except KeyboardInterrupt:
			# 如果捕获到键盘中断异常，则输出信息并退出程序
			print("KeyboardInterrupt")
			sys.exit()
		except Exception as err:
			# 其他异常，输出错误信息
			print(err)


def read_file(file_path):
	"""
		读取文件内容并返回字符串

		参数:
			file_path (str): 文件路径

		返回值:
			str: 去除首尾的空格和换行符的文件内容字符串表示

		异常:
			FileNotFoundError: 如果文件不存在或不是文件
		"""
	file_path = Path(file_path)
	if not file_path.is_file():
		raise FileNotFoundError(f"文件不存在或不是文件: {file_path}")
	with file_path.open("r") as file:
		return file.read().strip()


# 定义函数 SinglePython_cmd()
def single_python_cmd():
	"""
		这个函数用于运行单个 Python 命令。
		它处理目录切换、文件读取和变量默认值的设置。
	"""
	# 获取运行脚本的绝对路径，并将它赋值给局部变量 runpath
	runpath = os.path.dirname(os.path.realpath(sys.argv[0]))

	try:
		# 尝试进入以下两个目录：
		# 1. "{runpath}/SinglePython_files/userdata/"
		# 2. "{runpath}/SinglePython_files/cmd"
		# 如果进入失败，会抛出异常并跳转到 except 部分执行。
		os.chdir(f"{runpath}/SinglePython_files/userdata/")
		os.chdir(f"{runpath}/SinglePython_files/cmd")
	except Exception:
		while True:
			# 循环提示用户输入命令，如果用户输入 exit，则退出程序；
			initcmd = input("(InstallationENV) ")
			if initcmd == 'exit':
				exit()

	try:
		# 读取默认登录用户文件，获取用户名并去除首尾空格
		default_login_user_file = read_file(f"{runpath}/SinglePython_files/userdata/defaultloginuser").strip()
		# 创建用户主目录，如果不存在则创建
		os.makedirs(f"{runpath}/SinglePython_files/userdata/home/{default_login_user_file}", exist_ok=True)
	except FileNotFoundError:
		# 捕获文件不存在的异常，设置默认用户名为'user'
		cmd_username = 'user'

	try:
		# 读取主机名文件，获取主机名并去除首尾空格
		cmd_hostname = read_file(f"{runpath}/SinglePython_files/hostname/hostname").strip()
	except FileNotFoundError:
		# 捕获文件不存在的异常，设置默认主机名为'SinglePython'
		cmd_hostname = "SinglePython"


# 帮助信息
helpinfo = """
用法: SinglePython [OPTIONS]

Options:
  -f --file   输入 Python 文件名并运行（*.py）
  -h --help   显示帮助信息
  -v --version  显示 SinglePython 版本信息
"""


# 定义函数handle_option，用于处理命令行选项
def handle_option(opt_name: str, opt_value: str = None) -> None:
	"""
	根据选项名称处理不同的选项。

	参数:
		opt_name (str): 选项的名称。
		opt_value (str, 可选): 与选项关联的值。默认为 None。
	"""

	# 检查是否是帮助信息选项
	if opt_name in ('-h', '--help'):
		# 打印帮助信息并退出程序
		print(helpinfo)
		sys.exit(0)

	# 检查是否是版本信息选项
	elif opt_name in ('-v', '--version'):
		# 打印版本信息并退出程序
		print(color_print(
			f"SinglePython {SinglePythonInfo['version']}-{SinglePythonInfo['releases_version']}, 使用 Python {platform.python_version()}",
			'cyan'))
		sys.exit(0)

	# 检查是否是指定文件执行选项
	elif opt_name in ('-f', '--file'):
		# 获取文件名，如果参数值为空则使用空字符串作为文件名
		filename = opt_value if opt_value is not None else ''
		# 执行读取文件的函数
		optreadfile_exec(filename)
		# 程序退出
		sys.exit()

	else:
		# 如果不是帮助信息选项，也不是版本信息选项，也不是指定文件执行选项，则抛出异常
		raise GetoptError(opt_name)


# 使用 getopt 库处理命令行参数
try:
	"""
	设置可选参数及其对应的短选项和长选项：
	-h 对应 --help，用于显示帮助信息
	-f 对应 --file=，后面可以接一个文件名作为参数
	-v 对应 --version，用于显示版本信息
	"""
	opts, args = getopt(sys.argv[1:], 'hf:v', ['help', 'file=', 'version'])
	# 遍历opts中的每个元素（一个元组），将每个元组的第一个元素作为参数传递给handle_option函数
	for opt_name, opt_value in opts:
		handle_option(opt_name, opt_value)
# 处理可能出现的 getopt 错误
except GetoptError as err:
	# 输出错误信息：您使用的参数不存在或未完全输入，请查看帮助!!!
	print(f"{color_print('参数错误:', 'red')} {str(err)}")
	# 输出帮助信息
	print(helpinfo)
	# 退出程序
	sys.exit(2)  # 参数错误时，程序异常结束，返回值为2

try:
	# 显示欢迎文本
	show_startup_info()
	# 直接进入 SinglePython_shell 主界面
	SinglePython_shell()
except Exception as e:
	# 如果发生任何异常，打印错误信息并退出程序
	print(f"{color_print("An error occurred:", 'red')} {str(e)}")
	sys.exit(1)
