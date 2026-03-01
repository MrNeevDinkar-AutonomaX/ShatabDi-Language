import sys
import re
import pickle
import os

variables = {}
functions = {}
modules_loaded = set()

# ================= TOKENIZER =================

def tokenize(expr):
    return re.findall(r'\d+|".*?"|\w+|==|!=|>=|<=|[+\-*/()<>]', expr)

# ================= BYTECODE =================

def compile_to_bytecode(lines):
    bytecode = []
    for line in lines:
        bytecode.append(line.strip())
    return bytecode

def run_bytecode(bytecode):
    execute_block(bytecode)

def save_bytecode(filename, bytecode):
    with open(filename + ".sbc", "wb") as f:
        pickle.dump(bytecode, f)

def load_bytecode(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

# ================= ARG SPLIT =================

def split_args(s):
    args = []
    depth = 0
    current = ""
    for c in s:
        if c == "," and depth == 0:
            args.append(current)
            current = ""
        else:
            if c == "(": depth += 1
            if c == ")": depth -= 1
            current += c
    if current:
        args.append(current)
    return args

# ================= EXPRESSION ENGINE =================

def eval_expression(tokens):
    def parse(index=0):
        values = []
        ops = []

        def apply():
            r = values.pop()
            l = values.pop()
            o = ops.pop()
            values.append(eval_op(l,o,r))

        prec = {
            "==":1,"!=":1,">":1,"<":1,">=":1,"<=":1,
            "+":2,"-":2,
            "*":3,"/":3
        }

        while index < len(tokens):
            t = tokens[index]

            if t.isdigit():
                values.append(int(t))

            elif t.startswith('"'):
                values.append(t[1:-1])

            elif t in variables:
                values.append(variables[t])

            elif t == "(":
                val,index = parse(index+1)
                values.append(val)

            elif t == ")":
                break

            elif t in prec:
                while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                    apply()
                ops.append(t)

            index += 1

        while ops:
            apply()

        return values[0], index

    result,_ = parse()
    return result

def eval_op(l,o,r):
    if o=="+": return l+r
    if o=="-": return l-r
    if o=="*": return l*r
    if o=="/": return l/r
    if o=="==": return l==r
    if o=="!=": return l!=r
    if o==">": return l>r
    if o=="<": return l<r
    if o==">=": return l>=r
    if o=="<=": return l<=r

# ================= EVALUATE =================

def evaluate(expr):
    expr = expr.strip()

    if expr == "input()":
        return input()

    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]

    if re.match(r"\w+\(.*\)", expr):
        m = re.search(r"(\w+)\((.*?)\)", expr)
        name = m.group(1)
        args_raw = m.group(2)

        args = []
        if args_raw.strip():
            args = split_args(args_raw)

        args = [evaluate(a.strip()) for a in args]

        if name in functions:
            params, block = functions[name]
            old = variables.copy()

            for p,a in zip(params,args):
                variables[p]=a

            result = execute_block(block)

            variables.clear()
            variables.update(old)
            return result

    return eval_expression(tokenize(expr))

# ================= IMPORT SYSTEM =================

def import_module(name):
    if name in modules_loaded:
        return

    filename = name + ".ShatabDi"
    if os.path.exists(filename):
        with open(filename) as f:
            execute_block(f.readlines())
        modules_loaded.add(name)
    else:
        print("Module not found:", name)

# ================= EXECUTION =================

def execute_block(lines):
    i=0
    while i<len(lines):
        line = lines[i].strip()

        if "#" in line:
            line = line.split("#")[0].strip()

        if not line:
            i+=1
            continue

        if line.startswith("import"):
            mod = line.split()[1]
            import_module(mod)

        elif line.startswith("print"):
            print(evaluate(line[5:].strip()))

        elif line.startswith("let"):
            var,val = line[3:].strip().split("=",1)
            variables[var.strip()] = evaluate(val.strip())

        elif line.startswith("func"):
            m = re.search(r"func (\w+)\((.*?)\) {", line)
            name = m.group(1)
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            block=[]
            i+=1
            while i<len(lines) and lines[i].strip()!="}":
                block.append(lines[i])
                i+=1
            functions[name]=(params,block)

        elif line.startswith("return"):
            return evaluate(line[7:].strip())

        elif line.startswith("if"):
            cond = re.search(r"if (.*) {", line).group(1)
            block=[]
            i+=1
            while i<len(lines) and lines[i].strip()!="}":
                block.append(lines[i])
                i+=1
            if evaluate(cond):
                execute_block(block)

        elif line.startswith("loop"):
            count = evaluate(line.split()[1])
            block=[]
            i+=1
            while i<len(lines) and lines[i].strip()!="}":
                block.append(lines[i])
                i+=1
            for _ in range(int(count)):
                execute_block(block)

        elif re.match(r"\w+\(.*\)", line):
            evaluate(line)

        i+=1

# ================= SMART REPL =================

def repl():
    print("ShatabDi 4.0 REPL")
    buffer=[]
    brace_count=0

    while True:
        prompt=">>> " if brace_count==0 else "... "
        line=input(prompt)

        if line=="exit":
            break

        brace_count += line.count("{")
        brace_count -= line.count("}")

        buffer.append(line)

        if brace_count==0:
            execute_block(buffer)
            buffer=[]

# ================= MAIN =================

if __name__=="__main__":

    if len(sys.argv)==2:

        if sys.argv[1].endswith(".sbc"):
            bytecode = load_bytecode(sys.argv[1])
            run_bytecode(bytecode)

        elif sys.argv[1].endswith(".ShatabDi"):
            with open(sys.argv[1]) as f:
                lines=f.readlines()
            bytecode=compile_to_bytecode(lines)
            run_bytecode(bytecode)

        else:
            print("ShatabDi only runs .ShatabDi or .sbc")

    else:
        repl()