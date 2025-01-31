import code


class MyInteractiveInterpreter(code.InteractiveInterpreter):
    def __init__(self):
        super().__init__()
        self.buffer = []

    def runsource(self, source, filename="<input>", symbol="exec"):
        self.buffer.append(source)
        source = "\n".join(self.buffer)
        if code.compile_command(source) is not None:
            self.buffer = []
            return super().runsource(source, filename, symbol)
        return True
