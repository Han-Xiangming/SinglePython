# SinglePtyhon
ver = "0.51"

libs_warning = "1"
# 1 is ture 0 is false.
# 将值更改为 0 将关闭库不存在的提示


releases_ver = "official"
importlibs = "os"


class SinglePythoninfo:
	def ver(self):
		print(ver)

	def libs_warning(self):
		print(libs_warning)

	def releases_ver(self):
		print(releases_ver)

	def build_importlibs(self):
		print(importlibs)


# 获取系统信息（Windows或Linux...）
import platform

sys = platform.system()
if sys == "Windows":
	class SinglePythonwin:
		def set_console_title(self):
			import ctypes
			ctypes.windll.kernel32.SetConsoleTitleW(f"SinglePython {ver}")


	win = SinglePythonwin()
	win.set_console_title()


# SinglePython自导入功能
def self_import(name):
	__import__(name)


# sourcery skip: use-contextlib-suppress
try:
	self_import(importlibs)
except ImportError:
	if libs_warning == "1":
		print(
			f"Warning: Custom import library {importlibs} does not exist, please check the source code library configuration and rebuild"
		)
		print("")

try:
	# 基础导入
	import getopt
	import sys
	import platform
	import os
	import cmd
	import random
	import requests
except Exception:
	print("SinglePython Error: Import Error")
	sys.exit()


# 运行 Python 文件选项（-f）
def optreadfile():
	getfile = sys.argv[1]
	with open(getfile, encoding="utf-8") as f:
		code = f.read()
		compiled_code = compile(code, file, "exec")
		exec(compiled_code)
	sys.exit(0)


# Main
def SinglePython_welcome_text():
	print(
		f"SinglePython {ver}-{releases_ver} (Python Version:{platform.python_version()}) [Running on {platform.platform()} {platform.version()}]"
	)


def SinglePython_shell():
	def cls():
		os.system('cls' if os.name == 'nt' else 'clear')
		SinglePython_welcome_text()

	def clear():
		os.system('cls' if os.name == 'nt' else 'clear')
		SinglePython_welcome_text()

	while True:
		try:
			multiline_input = False
			input_buffer = ""

			while True:
				prompt = "..." if multiline_input else ">>> "
				user_input = input(prompt)
				input_buffer += user_input + "\n"

				if user_input.strip() == "":
					multiline_input = False
				elif user_input.strip().endswith(":"):
					multiline_input = True
				else:
					multiline_input = False
				if user_input == "exit":
					sys.exit()
				elif user_input in ('cls', 'clear'):
					errorinfo = os.system('cls' if os.name == 'nt' else 'clear')
					SinglePython_welcome_text()
				if not multiline_input:
					try:
						exec(input_buffer)
						input_buffer = ""
					except Exception as e:
						print(f"Error: {e}")
						input_buffer = ""
		except KeyboardInterrupt:
			print("KeyboardInterrupt")
			sys.exit()
		except Exception as err:
			print(err)


def SinglePython_cmd():
	global runpath
	runpath = os.path.dirname(os.path.realpath(sys.argv[0]))
	try:
		os.chdir(f"{runpath}/SinglePython_files/userdata/")
		os.chdir(f"{runpath}/SinglePython_files/cmd")
	except Exception:
		while True:
			initcmd = input("(InstallationENV) ")
			if initcmd == 'exit':
				exit()
			if initcmd == 'shell':
				break
	try:
		global cmd_username
		default_profile = open(
			f"{runpath}/SinglePython_files/userdata/defaultloginuser", "r"
		)
		cmd_username = default_profile.read()
		os.chdir(f"{runpath}/SinglePython_files/userdata/home/{cmd_username}")
	except Exception:
		cmd_username = 'user'
		print(
			'无法切换到 SinglePython 用户配置文件：找不到默认用户。要使用临时目录用户，请使用“adduser”和“setdefaultuser<username>”创建用户并设置默认用户')
	try:
		get_hostname = open(f"{runpath}/SinglePython_files/hostname/hostname", "r")
		cmd_hostname = get_hostname.read()
	except Exception:
		cmd_hostname = "SinglePython"


# 打印所有帮助信息
helpinfo = """
用法: SinglePython [OPTIONS]

Options:
-f            --file               输入 Python 文件名并运行 （*.py），但此选项无运行完成提示
-h            --help               查看帮助
-v            --version            查看SinglePython版本
"""

# getopt
try:
	# 设置选项
	opts, args = getopt.getopt(sys.argv[1:], '-h:-f:-v',
	                           ['help', 'file=', 'version'])
# 设置getopt错误提示
except getopt.GetoptError as err:
	print("请查看帮助：")
	print("您使用的参数不存在或未完全输入，请查看帮助!!!")
	print(helpinfo)
	sys.exit()
# 获取每个选项并运行
for opt_name, opt_value in opts:
	if opt_name in ('-h', '--help'):
		# -h 显示完整帮助功能
		print(helpinfo)
		sys.exit()
	if opt_name in ('-v', '--version'):
		# -v 显示版本
		print(f"SinglePython {ver}-{releases_ver}")
		print(f"Python {platform.python_version()}")
		sys.exit()
	if opt_name in ('-f', '--file'):
		# -f 运行文件
		file = opt_value
		with open(file, encoding="utf-8") as f:
			code = f.read()
			compiled_code = compile(code, file, "exec")
			exec(compiled_code)
		sys.exit()

# go main shell
try:
	SinglePython_welcome_text()
	with open("startupfile.conf", encoding="utf-8") as filename:
		startupcode = filename.read()
	exec(startupcode)
except Exception:
	SinglePython_shell()
