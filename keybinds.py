# Default keybindings provided by the client
CtrlKeyDownActions = {
    "Numpad1": ["DAE sw"],"Numpad2": ["DAE s"],"Numpad3": ["DAE se"],"Numpad4": ["DAE w"],"Numpad5": ["look"],
    "Numpad6": ["DAE e"],"Numpad7": ["DAE nw"],"Numpad8": ["DAE n"],"Numpad9": ["DAE ne"]}    

AltKeyDownActions = {
    "Numpad1": ["DAO sw"],"Numpad2": ["DAO s"],"Numpad3": ["DAO se"],"Numpad4": ["DAO w"],"Numpad5": ["look"],
    "Numpad6": ["DAO e"],"Numpad7": ["DAO nw"],"Numpad8": ["DAO n"],"Numpad9": ["DAO ne"]}    

KeyDownActions = {
    "Numpad1": ["sw",],"Numpad2": ["s"],"Numpad3": ["se"],"Numpad4": ["w"],"Numpad5": ["look"],
    "Numpad6": ["e"],"Numpad7": ["nw"],"Numpad8": ["n"],"Numpad9": ["ne"],"NumpadAdd": ["mome_","temu","x all"],"NumpadSubtract": ["DA_WAE"],
    "NumpadDivide":["DA_OUT"]}

#
# Keybindings here override defaults and are applied per room-info ID:
# 

key_binds={
  4132565139:  {  'F4':["Sc","d","e","s","e","2 s","se","5 s","e"],
                  'F8':["Rift","d","e","s","e","s","6 e","s","e","2 s","2 w"],
                  'F6':["Shanty","d","e","s","e","5 n","2 w","s","3 w","2 sw","w","sw","4 w","nw","3 w","nw","5 w","3 nw","3 n","6 nw","12 w","path","town","gate"],
}, 4181828127: {  'F4':["Sc","s","4 w","4 s","se","5 s","e"],
                  'F6':["Shanty","s","4 w","3 n","2 w","s","3 w","2 sw","w","sw","4 w","nw","3 w","nw","5 w","3 nw","3 n","6 nw","12 w","path","town","gate"],
                  'F7':["Sewer","s","2 w","2 n","w","2 d"],
                  'F8':["Rift","3 s","2 e","n","advance","store","3 s","e","2 s","2 w"],            
}, 573688540:  {  'F4':["Sc","4 e","sw","7 w","3 s","e"],
                  'F7':["Bank","2 e","2 n","w","2 n","5 w","sell noeq","e","2 n","2 w","sell noeq","3 e","2 n","dep"],
                  'F8':["inn","2 e","2 n","w","n","6 w","n","w","n","w","u"],
}, 4170434472: {  'F4':["Sc","s","out","e","se","s","s","se","e","ne","e","2 se","4 e","5 se","4 e","5 se","s","5 se","3 s","3 se","10 sw","2 s","sw","16 w","3 sw","9 w","2 sw","21 w","3 sw","2 w","nw"],
}, 1324508582: {  'F4':["Sc","out","e","se","s","s","se","e","ne","e","2 se","4 e","5 se","4 e","5 se","s","5 se","3 s","3 se","10 sw","2 s","sw","16 w","3 sw","9 w","2 sw","21 w","3 sw","2 w","nw"],
                
}, 1870850679: {  'F4':["Sc","s","se","e","ne","e","2 se","4 e","5 se","4 e","5 se","s","5 se","3 s","3 se","10 sw","2 s","sw","16 w","3 sw","9 w","2 sw","21 w","3 sw","2 w","nw"],
}, 1499883109: {  'F4':["Sc","u","n","e","2 s","se","5 s","e"],
                  'F8':["Rift","u","n","e","s","6 e","s","e","2 s","2 w"],
}, 3437892367: {  'F4':["Sc","sw","sw","s","se","3 sw","se","sw","6 s","5 sw","6 w","10 sw","4 s","16 sw","2 s","sw","16 w","3 sw","9 w","2 sw","21 w","3 sw","2 w","nw"],   
}, 2954911565: {  'F5':["Refugee","2 s","sw","s","2 sw","3 s","2 sw","w","3 sw","22 w","7 sw","4 s","sw","s","4 sw","s","sw","s","3 sw","3 s","2 sw","3 s","se","4 s","se","s","se","2 s","2 se","2 e","se","e","3 se","3 s","2 sw","s","2 sw","4 s","se","3 s","2 sw","s","sw"],
                  'F8':['sell',"get glows","3 get armours","3 get weapons","2 s","sw","s","2 sw","3 s","2 sw","w","3 sw","10 se","17 e","7 e","ne","3 n","ne","5 n","3 ne","nw","12 w","sell noeq","3 e","ne","nw","6 w","sell noeq","6 e","2 se","11 e","4 se","e","dep","w","2 s","3 sw","3 w","sw","s","sw","2 w","2 sw","7 w","17 w","10 nw","3 ne","e","2 ne","3 n","2 ne","n","ne","2 n"],   
}, 3192192722: {  'F5':["Refugee","17 w","10 nw","22 w","7 sw","4 s","sw","s","4 sw","s","sw","s","3 sw","3 s","2 sw","3 s","se","4 s","se","s","se","2 s","2 se","2 e","se","e","3 se","3 s","2 sw","s","2 sw","4 s","se","3 s","2 sw","s","sw"]
}, 1134116747: {  'F5':["Efreeti","se","2 e","3 ne","21 e","2 ne","9 e", "3 ne","16 e","ne","2 n","10 ne","3 nw","3 n","5 nw","n","5 nw","4 w","5 nw","4 w","2 nw","w","sw","w","nw","n","path","nw","w","crawl through crack"],
                  'F7':["Bank","nw","4 n","nw","n","4 e","n","3 w","sell noeq","e","2 n","2 w","sell noeq","3 e","2 n","dep"],
                  'F8':["Rift","nw","2 n","7 e","ne","4 w"],       
}, 2559517210: {  'F6':["makkis","ne","n","2 ne","3 n","nw","4 n","2 ne","n","2 ne","3 n","3 nw","w","nw","2 w","2 nw","2 n","nw","n","nw","4 n","nw","3 n","2 ne","3 n","3 ne","n","ne","n","4 ne","n","ne","4 n","7 ne","5 nw","3 ne","6 e","17 ne","7 n","12 ne","16 n","23 ne","21 n","11 ne","14 e","3 ne","5 n"],
                  'F7':["Klore","ne","n","2 ne","3 n","nw","4 n","2 ne","n","2 ne","3 n","3 nw","w","nw","2 w","2 nw","2 n","nw","n","nw","4 n","nw","3 n","2 ne","3 n","3 ne","n","ne","n","4 ne","n","ne","4 n","7 ne","22 e","3 ne","e","2 ne","3 n","2 ne","n","ne","2 n"],
                  'Numpad5':["Path","path"],
}, 2478180382: {  'F7':["Bank","2 u","2 e","2 s","2 e","2 s","3 w","sell noeq","e","2 n","2 w","sell noeq","3 e","2 n","dep"],
}, 2335991698: {  'F8':["Bank","out","road","road","12 e","6 se","3 s","3 se","5 e","se","3 e","se","4 e","ne","e","2 ne","3 e","n","2 e","3 s","4 e","2 s","3 w","sell noeq","e","2 n","2 w","sell noeq","3 e","2 n","dep"],
}, 3037593790: {  'F8':["Bank","12 e","6 se","3 s","3 se","5 e","se","3 e","se","4 e","ne","e","2 ne","3 e","n","2 e","3 s","4 e","2 s","3 w","sell noeq","e","2 n","2 w","sell noeq","3 e","2 n","dep"],
}, 3311899503: {  'F8':['sell',"get glows","3 get armours","3 get weapons","se","ne","n","2 ne","3 n","nw","4 n","2 ne","n","2 ne","3 n","3 nw","w","nw","2 w","2 nw","2 n","nw","n","nw","4 n","nw","3 n","2 ne","3 n","3 ne","n","ne","n","4 ne","n","ne","4 n","7 ne","22 e","10 se","17 e","ride dismount","7 e","ne","3 n","ne","5 n","3 ne","nw","12 w","sell noeq","3 e","ne","nw","6 w","sell noeq","6 e","2 se","11 e","4 se","e","dep","w","2 s","3 sw","3 w","sw","s","sw","2 w","2 sw","7 w","ride morty","17 w","10 nw","22 w","7 sw","4 s","sw","s","4 sw","s","sw","s","3 sw","3 s","2 sw","3 s","se","4 s","se","s","se","2 s","2 se","2 e","se","e","3 se","3 s","2 sw","s","2 sw","4 s","se","3 s","2 sw","s","sw","nw"],
}, 3217275705: {  'Numpad6': ['Tent','enter tent'], 
                  'Numpad8': ['Wall','climb wall'],
}, 1282588022: {  'Numpad4': ['Out','out'],
}, 2594813408: {  'Numpad8': ['Climb','climb grayish spruce'],
}, 3044815192: {  'Numpad2': ['Down','d'],
}, 1266008367: {  'Numpad8': ['Inhale','inhale mist'],
}, 590069385:  {  'Numpad2': ['Inhale','inhale mist'],
}, 3636149278: {  'Numpad6': ['Shack','shack']
}, 98455397:   {  'Numpad2': ['Wall','climb wall']
}, 2267176582: {  'Numpad4': ['Out','out']
}, 1650122953: {  'Numpad4': ['Tent','tent']
}, 2752659316: {  'Numpad8': ['Bush','move bush','n']
}, 1901731623: {  'Numpad2': ['Woods','woods']
}, 4139973774: {  'Numpad6': ['Search','search eastern wall','e'],
}, 3931898241: {  'Numpad6': ['Out','out'],
}, 463730410:  {  'Numpad6': ['Backroom','backroom'],
}, 2734606472: {  'Numpad4': ['Bar','bar'],
                
}
}
 
