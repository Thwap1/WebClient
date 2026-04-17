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

starts_with, ends_with = {},{}

def match_color_start(data):
    MOB_COLORS = {'wounded': 30, 'mob': 36, 'agro': 31}
    color = None
    i = 0
    while data.startswith(b'\033[', i):
        end = data.find(b'm', i + 2)
        if end == -1:
            break       
        codes = data[i + 2:end].split(b';')

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
         
    # if monster needs to be lited / handle gathered
    if color in MOB_COLORS.values():
        #mirror images parse
        i = 0
        if  len(data) > 9: 
            if '0' <= data[i] <= '9':
                i+=1
                if '0' <= data[i] <= '9':
                    i+=1
                if data[i:i+7]==" times ":
                    i+=7
                else:
                    i=0
                            
                            
        if (match:= monster_search(data[i:])):                
            return (COLORS['bright_blue'] + data + COLORS['reset']+"\n",match)

lookup_end_to_start, lookup_start_to_end, monster_search_table = {},{},{}

for w in starts_with:
    table = lookup_start_to_end
    for l in w:
        if l not in table:
            table[l] = {}
        table = table[l]
    table["$"] = starts_with[w]

for w in ends_with:
    table = lookup_end_to_start
    i = len(w) - 1
    while i>=0:
        if w[i] not in table:
            table[w[i]] = {}
        table = table[w[i]] 
        i-=1
    table["$"] = ends_with[w]

              

def monster_search(data):
    table = monster_search_table
    for letter in data:
        if letter in table:
            table = table[letter]
        else:
           # even partial match can be match since there could be multiple matches and if '$' exists it has matched to some trig
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
    table = lookup_end_to_start
    i = len(data) - 1
    while i>=0:
        if data[i] in table:
            table = table[data]
            i-=1
        else:
            break
    if '$' in table:
        return table['$']
    return False

def load():
    
    monster_search_table = {}
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
    

load()

 