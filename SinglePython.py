# 定义 SinglePython 的版本号
ver = "0.53"
# 定义变量，用以判断是否开启对库缺失的警告提示
libs_warning = "1"
# 0 表示不开启警告，1 表示开启警告。建议将此值设为 1，保持提醒


releases_ver = "official"
importlibs = "os"


class SinglePythonInfo:
	def __init__(self, ver, libs_warning, releases_ver, importlibs):
		"""
    	SinglePythonInfo类构造函数

		参数:
		- ver: str, Python版本号
		- libs_warning: list, 包含警告的库列表
		- releases_ver: str, 发布的版本号
		- importlibs: list, 导入的库列表
		"""
		self.ver = ver
		self.libs_warning = libs_warning
		self.releases_ver = releases_ver
		self.build_importlibs = importlibs

	def ver(self):
		print(self.ver)

	def libs_warning(self):
		print(self.libs_warning)

	def releases_ver(self):
		print(self.releases_ver)

	def build_importlibs(self):
		print(self.build_importlibs)


# 尝试基础导入所需模块，包括 getopt, sys, platform, os
try:
	from getopt import getopt, GetoptError  # 导入 getopt 和 GetoptError 异常
	import sys  # 导入 sys 模块
	import platform  # 导入 platform 模块
	import os  # 导入 os 模块
# 如果发生异常
except Exception:
	# 输出错误信息，并退出程序
	print("SinglePython Error: Import Error")  # 打印错误信息
	sys.exit()  # 退出程序

# 获取操作系统类型
sysinfo = platform.system()

# 如果是 Windows 系统，则定义 SinglePythonWin 类，用于设置控制台标题
if sysinfo == "Windows":
	class SinglePythonwin:
		# set_console_title 方法用于设置控制台标题
		def set_console_title(self):
			import ctypes
			# 使用 ctypes 库设置控制台标题
			ctypes.windll.kernel32.SetConsoleTitleW(f"SinglePython {ver}")


	# 创建 SinglePythonwin 对象，并调用其 set_console_title 方法设置控制台标题
	win = SinglePythonwin()
	win.set_console_title()


# 定义 self_import 函数，用于自导入指定的名字空间
def self_import(name):
	# 使用 __import__() 内置函数导入名字空间
	__import__(name)


# 尝试自导入用户提供的库
try:
	self_import(importlibs)
# 如果引发 ImportError 异常
except ImportError:
	# 如果 libs_warning 变量等于 "1"，则打印出警告信息，提示用户检查源代码库配置并重新构建
	if libs_warning == "1":
		print(f"Warning: 自定义导入库 {importlibs} 不存在，请检查源代码库配置并重新构建")
		print("")


# 定义 optreadfile_exec 函数，用于运行指定文件中的 Python 代码
def optreadfile_exec(filename):
	# 尝试打开文件并执行其中的 Python 代码
	try:
		with open(filename, "r") as f:
			exec(f.read())
		print(" ")
		print("Run Python file successfully")  # 如果出现文件未找到的错误
	except FileNotFoundError:
		# 输出错误信息
		print("SinglePython Error: 文件未找到")


# 定义 show_startup_info 函数，用于显示欢迎信息
def show_startup_info():
	# 打印 SinglePython 版本，Python 版本和运行环境等信息
	print(
		f"SinglePython {ver}-{releases_ver} (Python Version:{platform.python_version()}) [Running on {platform.platform()} {platform.version()}]")


# 定义 SinglePython_shell 函数，提供交互式 Python 解释器
# 定义SinglePython_shell函数，循环接收用户输入并执行
def SinglePython_shell():
	# 循环接收用户输入并执行
	while True:
		try:
			# 初始化多行输入标志
			multiline_input = False
			input_buffer = ""
			# 循环读取用户输入
			while True:
				# 根据 multiline_input 设置提示符号
				prompt = "..." if multiline_input else ">>> "
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
				# 如果用户输入为 "exit"，结束程序
				if user_input == "exit":
					sys.exit()
				# 如果用户输入为 "cls" 或 "clear"，清屏并重置欢迎信息
				elif user_input in ('cls', 'clear'):
					# 如果用户的输入是'cls'或'clear'
					def cls():
						# 定义一个函数cls，该函数不执行任何操作
						pass

					def clear():
						# 定义一个函数clear，该函数不执行任何操作
						pass

					os.system('cls' if os.name == 'nt' else 'clear')
					# 根据操作系统类型执行不同的命令，'cls'用于Windows操作系统，'clear'用于其他操作系统
					show_startup_info()
					# 调用show_startup_info函数显示启动信息
					continue

				# 如果用户输入中含有 ".py"，尝试执行指定的文件
				elif '.py' in user_input:
					user_input = str(user_input).replace('"', '')
					optreadfile_exec(user_input)
					continue
				# 如果不是多行输入，则尝试执行缓冲区内的代码
				if not multiline_input:
					try:
						exec(input_buffer)
						# 清空缓冲区
						input_buffer = ""
					except Exception as e:
						# 执行时遇到异常，打印错误信息并继续读取下一条命令
						print(f"Error: {e}")
						input_buffer = ""
		except KeyboardInterrupt:
			# 如果捕获到键盘中断异常，则输出信息并退出程序
			print("KeyboardInterrupt")
			sys.exit()
		except Exception as err:
			# 其他异常，输出错误信息
			print(err)


# 定义函数 SinglePython_cmd()
def SinglePython_cmd():
	# 获取运行脚本的绝对路径，并将它赋值给全局变量 runpath
	global runpath
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
		global cmd_username
		# 打开文件 "{runpath}/SinglePython_files/userdata/defaultloginuser" 并读取内容，将读取的内容赋值给全局变量 cmd_username
		with open(f"{runpath}/SinglePython_files/userdata/defaultloginuser", "r") as f:
			cmd_username = f.read().strip()
		# 创建用户的主目录，如果目录已存在则不报错
		os.makedirs(f"{runpath}/SinglePython_files/userdata/home/{cmd_username}", exist_ok=True)
	except FileNotFoundError:
		# 如果尝试进入用户主目录时出现异常，则将全局变量 cmd_username 赋值为 'user'
		cmd_username = 'user'
	try:
		# 打开文件 "{runpath}/SinglePython_files/hostname/hostname" 并读取内容，将读取的内容赋值给全局变量 cmd_hostname
		with open(f"{runpath}/SinglePython_files/hostname/hostname", "r") as f:
			cmd_hostname = f.read().strip()
	except FileNotFoundError:
		# 如果尝试获取主机名时出现异常，则将全局变量 cmd_hostname 赋值为 'SinglePython'
		cmd_hostname = "SinglePython"


# 帮助信息
helpinfo = """
用法: SinglePython [OPTIONS]

Options:
-f | --file   输入 Python 文件名并运行（*.py）
-h | --help   显示帮助信息
-v | --version  显示 SinglePython 版本信息
"""


# 定义函数handle_option，用于处理命令行选项
def handle_option(opt_name):
	# 检查是否是帮助信息选项
	if opt_name in ('-h', '--help'):
		# 打印帮助信息并退出程序
		print(helpinfo)
		sys.exit(0)
	# 检查是否是版本信息选项
	elif opt_name in ('-v', '--version'):
		# 打印版本信息并退出程序
		print(f"SinglePython {ver}-{releases_ver}, powered by Python {platform.python_version()}")
		sys.exit(0)
	# 检查是否是指定文件执行选项
	elif opt_name in ('-f', '--file'):
		# 获取指定的文件路径
		file = opt_value if opt_value is not None else ''
		try:
			# 读取文件内容并执行
			exec(open(file).read())
		except Exception as e:
			# 如果执行过程中出现异常，则打印错误信息并退出程序
			print(f"Error executing code from {file}: {e}")
		finally:
			# 无论是否出现异常，都要退出程序
			sys.exit()


# 使用 getopt 库处理命令行参数
try:
	# 设置可选参数及其对应的短选项和长选项：
	# -h 对应 --help，用于显示帮助信息
	# -f 对应 --file=，后面可以接一个文件名作为参数
	# -v 对应 --version，用于显示版本信息
	opts, args = getopt(sys.argv[1:], '-hf:-v', ['help', 'file=', 'version'])
	# 遍历opts中的每个元素（一个元组），将每个元组的第一个元素作为参数传递给handle_option函数
	for opt_name, opt_value in opts:
		handle_option(opt_name)
# 处理可能出现的 getopt 错误
except GetoptError as err:
	# 输出错误信息：您使用的参数不存在或未完全输入，请查看帮助!!!
	print(f"参数错误: {str(err)}")
	# 输出帮助信息
	print(helpinfo)
	# 退出程序
	sys.exit(2)  # 参数错误时，程序异常结束，返回值为2


try:
    # 显示欢迎文本
    show_startup_info()
    # 直接进入 SinglePython_shell 主界面
    SinglePython_shell()
except Exception:
    # 如果发生任何异常，打印错误信息并退出程序
    print("An error occurred:", sys.exc_info()[0])
    sys.exit(1)
