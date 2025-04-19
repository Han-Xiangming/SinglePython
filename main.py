# main.py

import sys
import time
import traceback
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm

from Core.config import SinglePythonInfo
from Core.shell import SinglePythonShell
from Core.utils import execute_code_from_file, get_version


def init():
    """
    初始化进度条显示。
    """
    print("Initializing...")
    for _ in tqdm(range(100), desc="Initialization", ncols=75, leave=False):
        time.sleep(0.001)  # 更快的进度条
    print("Initialization complete.")
    sys.stdout.write("\x1b[A" * 3)
    sys.stdout.flush()


def main():
    """
    主程序入口，解析命令行参数，执行文件或进入交互式 shell。
    """
    parser = ArgumentParser(description="Interactive Python Shell with additional features.")
    parser.add_argument("file", nargs='?', type=str, help="Execute Python code from the specified file")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after executing a file.")
    parser.add_argument("-v", "--version", action="version", version=get_version(), help="Show version information")
    args = parser.parse_args()

    try:
        if args.file:
            execute_code_from_file(args.file)  # 直接调用，无需线程池
            if args.interactive:
                shell = SinglePythonShell(SinglePythonInfo)
                init()
                shell.run()
            else:
                sys.exit(0)
        else:
            shell = SinglePythonShell(SinglePythonInfo)
            init()
            shell.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()