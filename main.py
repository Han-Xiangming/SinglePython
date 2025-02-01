import sys
import time
from argparse import ArgumentParser

from tqdm import tqdm

from Core.config import SinglePythonInfo
from Core.shell import SinglePythonShell
from Core.utils import execute_code_from_file, get_version


def init():
    print("Initializing...")
    for _ in tqdm(range(100), desc="Initialization", ncols=75):
        time.sleep(0.005)
    print("Initialization complete.")
    sys.stdout.write("\033[F\033[F\033[F")


def main():
    parser = ArgumentParser(description="Interactive Python Shell with additional features.")
    parser.add_argument("file", nargs='?', type=str, help="Execute Python code from the specified file")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after executing a file.")
    parser.add_argument("-v", "--version", action="version", version=get_version(), help="Show version information")
    args = parser.parse_args()

    try:
        if args.file:
            execute_code_from_file(args.file)
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
        sys.exit(1)


if __name__ == "__main__":
    main()
