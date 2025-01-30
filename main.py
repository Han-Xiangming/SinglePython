from argparse import ArgumentParser

from config import SinglePythonInfo
from shell import SinglePythonShell
from utils import get_version
from utils import optreadfile_exec


def main():
    parser = ArgumentParser(description="Interactive Python Shell with additional features.")
    parser.add_argument("-f", "--file", type=str, help="Execute Python code from the specified file")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Enter interactive mode after executing a file.")
    parser.add_argument("-v", "--version", action="version", version=get_version(), help="Show version information")
    args = parser.parse_args()

    try:
        if args.file:
            optreadfile_exec(args.file)
            if args.interactive:
                shell = SinglePythonShell(SinglePythonInfo)
                shell.run()
            else:
                sys.exit(0)
        else:
            shell = SinglePythonShell(SinglePythonInfo)
            shell.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
