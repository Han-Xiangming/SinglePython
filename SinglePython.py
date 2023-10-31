# 定义 SinglePython 的版本号
ver = "0.52"
# 定义变量，用以判断是否开启对库缺失的警告提示
libs_warning = "1"
# 0 表示不开启警告，1 表示开启警告。建议将此值设为 1，保持提醒


releases_ver = "official"
importlibs = "os"


# SinglePythonInfo 类用于获取SinglePython的相关信息
class SinglePythoninfo:
	# ver 方法用于打印 SinglePython 的版本号
	def ver(self):
		print(ver)

	# libs_warning 方法用于打印是否开启库不存在的提示
	def libs_warning(self):
		print(libs_warning)

	# releases_ver 方法用于打印发布版本信息
	def releases_ver(self):
		print(releases_ver)

	# build_importlibs 方法用于打印已导入库
	def build_importlibs(self):
		print(importlibs)


# 导入平台模块
import platform

# 获取操作系统类型
sys = platform.system()

# 如果是 Windows 系统，则定义 SinglePythonWin 类，用于设置控制台标题
if sys == "Windows":
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

# 尝试基础导入所需模块，包括 getopt, sys, platform, os, cmd, random 和 requests
try:
	import getopt
	import sys
	import platform
	import os
	import cmd
	import random
	import requests
# 如果发生异常
except Exception:
	# 输出错误信息，并退出程序
	print("SinglePython Error: Import Error")
	sys.exit()


# # 定义 optreadfile_exec 函数，用于运行指定文件中的 Python 代码
def optreadfile_exec(filename):
	# 尝试打开文件并执行其中的 Python 代码
	try:
		with open(filename, "r") as f:
			exec(f.read())
		print(" ")
		print("Run Python file successfully")
	# 如果出现异常
	except Exception:
		# 输出错误信息
		print("SinglePython Error: File not found")


# 定义 show_startup_info 函数，用于显示欢迎信息
def show_startup_info():
	# 打印 SinglePython 版本，Python 版本和运行环境等信息
	print(
		f"SinglePython {ver}-{releases_ver} (Python Version:{platform.python_version()}) [Running on {platform.platform()} {platform.version()}]"
	)


# 定义 SinglePython_shell 函数，提供交互式 Python 解释器
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
					errorinfo = os.system('cls' if os.name == 'nt' else 'clear')
					show_startup_info()
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
			# 循环提示用户输入命令，如果用户输入 exit，则退出程序；如果用户输入 shell，则跳出循环
			initcmd = input("(InstallationENV) ")
			if initcmd == 'exit':
				exit()
			if initcmd == 'shell':
				break
	try:
		global cmd_username
		# 打开文件 "{runpath}/SinglePython_files/userdata/defaultloginuser" 并读取内容，将读取的内容赋值给全局变量 cmd_username
		default_profile = open(
			f"{runpath}/SinglePython_files/userdata/defaultloginuser", "r"
		)
		cmd_username = default_profile.read()
		# 进入 "{runpath}/SinglePython_files/userdata/home/{cmd_username}" 目录
		os.chdir(f"{runpath}/SinglePython_files/userdata/home/{cmd_username}")
	except Exception:
		# 如果尝试进入用户主目录时出现异常，则将全局变量 cmd_username 赋值为 'user'
		cmd_username = 'user'
		# 输出错误信息：无法切换到 SinglePython 用户配置文件，因为找不到默认用户。要使用临时目录用户，请使用“adduser”和“setdefaultuser<username>”创建用户并设置默认用户
		print(
			'无法切换到 SinglePython 用户配置文件：找不到默认用户。要使用临时目录用户，请使用“adduser”和“setdefaultuser<username>”创建用户并设置默认用户')
	try:
		# 打开文件 "{runpath}/SinglePython_files/hostname/hostname" 并读取内容，将读取的内容赋值给全局变量 cmd_hostname
		get_hostname = open(f"{runpath}/SinglePython_files/hostname/hostname", "r")
		cmd_hostname = get_hostname.read()
	except Exception:
		# 如果尝试获取主机名时出现异常，则将全局变量 cmd_hostname 赋值为 'SinglePython'
		cmd_hostname = "SinglePython"


# 帮助信息
helpinfo = """
用法: SinglePython [OPTIONS]

Options:
-f | --file   输入 Python 文件名并运行（*.py），但此选项无运行完成提示
-h | --help   显示帮助信息
-v | --version  显示 SinglePython 版本信息
"""

# 使用 getopt 库处理命令行参数
try:
	# 设置可选参数及其对应的短选项和长选项：
	# -h 对应 --help，用于显示帮助信息
	# -f 对应 --file=，后面可以接一个文件名作为参数
	# -v 对应 --version，用于显示版本信息
	opts, args = getopt.getopt(sys.argv[1:], '-h:-f:-v',
							   ['help', 'file=', 'version'])
# 处理可能出现的 getopt 错误
except getopt.GetoptError as err:
	# 输出帮助信息
	print("请查看帮助：")
	# 输出错误信息：您使用的参数不存在或未完全输入，请查看帮助!!!
	print("您使用的参数不存在或未完全输入，请查看帮助!!!")
	# 输出帮助信息
	print(helpinfo)
	# 退出程序
	sys.exit()
# 处理每个选项
for opt_name, opt_value in opts:
	# 如果选项是 "-h" 或 "--help"，则显示完整帮助信息并退出程序
	if opt_name in ('-h', '--help'):
		# -h 显示完整帮助功能
		print(helpinfo)
		sys.exit()
	# 如果选项是 "-v" 或 "--version"，则显示版本信息并退出程序
	if opt_name in ('-v', '--version'):
		# -v 显示版本
		print(f"SinglePython {ver}-{releases_ver}")
		print(f"Python {platform.python_version()}")
		sys.exit()
	# 如果选项是 "-f" 或 "--file"，则运行指定的文件
	if opt_name in ('-f', '--file'):
		# 获取选项后面的文件名
		file = opt_value
		# 打开文件，并以 UTF-8 编码读取其内容
		with open(file, encoding="utf-8") as f:
			code = f.read()
			# 编译代码，得到编译后的对象
			compiled_code = compile(code, file, "exec")
			# 执行编译后的代码
			exec(compiled_code)
		# 退出程序
		sys.exit()

try:
	# 显示欢迎文本
	show_startup_info()
	# 直接进入 SinglePython_shell 主界面
	SinglePython_shell()
except Exception:
	# 如果发生任何异常，打印错误信息并退出程序
	print("An error occurred:", sys.exc_info()[0])
	sys.exit(1)