# First draft builds start/end triggers only.
# Triggers are loaded from the setup folder.
# Some trigger sets (e.g. monster names) are kept in separate files,
# such as color-specific variants, to avoid matching non-ANSI lines unnecessarily.
#
# No wildcards are used; triggers are implemented as nested hash tables,
# providing lightweight branching similar to regex-style alternatives
# like {this|that|asdf}, without full regex complexity.
# 
# UI-modifications to those will be implemented later
# possibly later folder with player namehash and restrictions how many triggers there too.
#
lookup_end_to_start, lookup_start_to_end, monster_search_table = {},{},{}
from common import FORMAT

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

COLORS = {
    "reset": "\033[0m",

    # Regular colors
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",

    # Bright colors
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",

    # Background colors
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
}

def match_color_start(container):
    og_data = container["og"]
    try:
        MOB_COLORS = {'wounded': 30, 'mob': 36, 'agro': 31}
        color = None
        i = 0
        while og_data.startswith(b'\033[', i):
            end = og_data.find(b'm', i + 2)
            if end == -1:
                break       
            codes = og_data[i + 2:end].split(b';')
            for c in codes:
                if c == b'1':
                    continue  # skip bold
                try:
                    val = int(c)
                except ValueError:
                    continue
                if val != 0:
                    color = val
                    break
            if color is not None:
                break
            i = end + 1 

        if color in MOB_COLORS.values(): # if monster needs to be lited / handle gathered
            data = container["text_data"]
            i = 0 #mirror images parse
            if  len(data) > 9: 
                if '0' <= data[i] <= '9':
                    i+=1
                    if '0' <= data[i] <= '9':
                        i+=1
                    if data[i:i+7]==" times ":
                        i+=7
                    else:
                        i=0            
            if (match:= monster_search(container["text_data"][i:])):
                container["og"] = (COLORS['bright_blue'] +  container["text_data"] + COLORS['reset']+"\n").encode(FORMAT)
                return match
    except Exception as e:
        print("colormatch error",e)

def monster_search(data):
    table = monster_search_table
    for letter in data:
        if letter in table:
            table = table[letter]
        else:
           break
    if '$' in table:
        return table['$']
            
        
    return False

#nested end and start tables for fast search.
def match_trigger_start_end(data):
    
    table = lookup_start_to_end
    for l in data:
        if l in table:
            table = table[l]
        else:
           break
    if '$' in table:
        return table['$']
    try:
        table = lookup_end_to_start
        i = len(data) - 1
        while i>=0:
            if data[i] in table:
                table = table[data[i]]
                i-=1
            else:
                break
        if '$' in table:
            return table['$']
        return False
    except Exception as e:
        print("startend lookup error",e)

def load_monster(): 
    global monster_search_table
    try:
        #file has monsters with syntax from start and then with ::: delim it has after that handle for that monster
        with open("setup/monsters.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":::" not in line:
                    continue
                syntax, monster_name = line.split(":::", 1)
                monster_name = monster_name.strip()
                table = monster_search_table
                for letter in syntax:
                    if letter not in table:
                        table[letter] = {}     
                    table = table[letter]
                table["$"] = monster_name
        
    except FileNotFoundError:
        pass  


mapper_remove_dirs = [
    "Your current coordinates are x:::#MAP_COORDS",
    "You decide to stop fleeing.:::#MAP_A",
    "You cannot do that while sleeping!:::#MAP_A",
    "You are already trying to flee from battle!:::#MAP_F",
    "Your access to the residence premises is denied.:::#MAP_1",
    "You can't go that way!:::#MAP_1",
    "The door is locked.:::#MAP_1",
    "You can't flee to:::#MAP_1",]
mapper_remove_end = {
    
    "blocks your way.:::#MAP_1",
    "blocks your way to east.:::#MAP_1",
}

def load_trig_start(): 
    global lookup_end_to_start
    try:
        #file has monsters with syntax from start and then with ::: delim it has after that handle for that monster
        
        with open("setup/trig_start.txt", "a+", encoding="utf-8") as f:
            f.seek(0)
            
            sources = [f]
            sources.append(mapper_remove_dirs)

            for data in sources:
                for line in data:
                    line = line.strip()
                    if ":::" not in line:
                        continue
                    syntax, what_to_do = line.split(":::", 1)
                    what_to_do = parse(what_to_do)
                    table = lookup_start_to_end
                    for letter in syntax:
                        if letter not in table:
                            table[letter] = {}     
                        table = table[letter]
                    if '$' in table:
                        table["$"].append(what_to_do)
                    else:
                        table["$"] = [what_to_do]
        with open("setup/trig_end.txt", "a+", encoding="utf-8") as f:
            f.seek(0)
            
            sources = [f]
            sources.append(mapper_remove_end)
            for data in sources:
                for line in data:
                    line = line.strip()
                    if ":::" not in line:
                        continue
                    syntax, what_to_do = line.split(":::", 1)
                    what_to_do = parse(what_to_do)
                    table = lookup_end_to_start
                    i = len(syntax) - 1
                    while i>=0:
                        if syntax[i] not in table:
                            table[syntax[i]] = {}
                        table = table[syntax[i]] 
                        i-=1
                    if '$' in table:
                        table["$"].append(what_to_do)
                    else:
                        table["$"] = [what_to_do]



    except FileNotFoundError:
        
        pass  




load_trig_start()
load_monster()




