



alias_list = {}

def parse(s):
    stack = [[]]
    token = ""

    i = 0
    while i < len(s):
        c = s[i]

        if c == "{":
            if token.strip():
                stack[-1].append(token.strip())
                token = ""

            stack.append([])

        elif c == "}":
            if token.strip():
                stack[-1].append(token.strip())
                token = ""

            completed = stack.pop()
            stack[-1].append(completed)

        elif c == ";":
            if token.strip():
                stack[-1].append(token.strip())
                token = ""

        else:
            token += c

        i += 1

    if token.strip():
        stack[-1].append(token.strip())

    return stack[0]

def load(): 
    global alias_list
    try:
        #file has monsters with syntax from start and then with ::: delim it has after that handle for that monster
        with open("setup/alias.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":::" not in line:
                    continue
                name, what_to_do = line.split(":::", 1)
                alias_list[name] = parse(what_to_do)
                
                
                
    except FileNotFoundError:
        pass  

load()

