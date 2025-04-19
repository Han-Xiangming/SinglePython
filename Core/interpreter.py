# interpreter.py

import code

class MyInteractiveInterpreter(code.InteractiveInterpreter):
    """
    扩展的交互式解释器，支持多行缓冲输入。
    """

    def __init__(self) -> None:
        super().__init__()
        self.buffer: list[str] = []

    def runsource(
        self, source: str, filename: str = "<input>", symbol: str = "exec"
    ) -> bool:
        """
        支持多行输入的代码缓冲与执行。
        :param source: 当前输入的代码行
        :param filename: 源文件名
        :param symbol: 执行类型
        :return: True 表示需要继续输入，False 表示已执行
        """
        self.buffer.append(source)
        source_joined = "\n".join(self.buffer)
        if code.compile_command(source_joined) is not None:
            self.buffer = []
            return super().runsource(source_joined, filename, symbol)
        return True