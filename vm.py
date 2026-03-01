class VM:
    def __init__(self):
        self.stack = []
        self.variables = {}

    def run(self, bytecode):
        pc = 0
        while pc < len(bytecode):
            instr = bytecode[pc]

            if instr[0] == "LOAD_CONST":
                self.stack.append(instr[1])

            elif instr[0] == "STORE_VAR":
                self.variables[instr[1]] = self.stack.pop()

            elif instr[0] == "LOAD_VAR":
                self.stack.append(self.variables[instr[1]])

            elif instr[0] == "ADD":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)

            elif instr[0] == "PRINT":
                print(self.stack.pop())

            pc += 1