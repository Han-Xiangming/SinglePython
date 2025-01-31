from argparse import ArgumentParser

from config import SinglePythonInfo
from shell import SinglePythonShell
from utils import execute_code_from_file
from utils import get_version


def main():
    parser = ArgumentParser(description="Interactive Python Shell with additional features.")
    parser.add_argument("-f", "--file", type=str, help="Execute Python code from the specified file")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after executing a file.")
    parser.add_argument("-v", "--version", action="version", version=get_version(), help="Show version information")
    args = parser.parse_args()

    try:
        if args.file:
            execute_code_from_file(args.file)
            if args.interactive:
                shell = SinglePythonShell(SinglePythonInfo)
                shell.run()
            else:
                sys.exit(0)
        else:
            shell = SinglePythonShell(SinglePythonInfo)
            shell.run()
    except Exception as e:
        from rich import traceback
        traceback.install(show_locals=True)
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
