import copy

debugMode = False
functionMode = False
content = 0

#current Line 
cLine = -1
skipNextLine = False
skipWhile = False
skipIf = False
# used to check when ifskip wheer i is he coresspponding Endif or not (while thhe same)
ifNester = 0
whileNester = 0

class DataType():
    def __init__(self, name, origin1, origin2,index):
        self.name = name
        self.origin1 = origin1
        self.origin2 = origin2
        self.index = index

class Variable():
    def __init__(self, name,type, origin1, origin2):
        self.name = name
        self.type = type
        self.origin1 = origin1
        self.origin2 = origin2
       
class Function():
    def __init__(self, name, begin, end):
        self.name = name
        self.begin = begin +1
        self.end = end
        self.parameterStack = []


variables = [ DataType("BIT",0,0,0)]
cache = [[]]
functions  = []

whiles = []
pos = -1


def GetType(name):
    return next ((v for v in variables if(v.name == name)),None)

def GetFunction(name):
     return next ((f for f in functions if(f.name == name)),None)
def GetVariable(name,f,convert):
    var = next(
        (cell for row in cache
         for cell in row
         if cell.name == name),
        None
    )
    if var != None or f == None: return var 
    name = ConvertName(name,f,convert)
    var = next(
        (cell for row in cache
         for cell in row
         if cell.name == name),
        None
    )
    return var
def DeleteVariable(name):
    var = next(
    (
        (row, cell)
        for row in cache
        for cell in row
        if cell.name == name
    ),
    (None, None)
    )

    row, cell = var

    if cell is not None:
        row.remove(cell)
    return var
def ConvertName(name,f,convert):
    l = len(f.parameterStack)
    for i in range (0,l):
        if name == f.parameterStack[i].name:
            return convert[i]
    return name
def Print(coms,f,convert):
    if(len(coms) != 2 ): Error("Print Wrong")
    v = GetVariable(coms[1],f,convert)
    if v == None: Error("NO Variable Found Print")
    if v.type !=  0: Error("Tried to Print a non BIT")
    if v.origin1  == 1: print("1")
    else: print (0)
def AddVariable( coms):

    if(len (coms) != 4): Error("NOT 4 COMMANDS WITH COMBINE")
    if (not any(coms[2] == p.name for p in variables )): Error("Variable unknown")
    if (not any(coms[3] == p.name for p in variables )): Error("Variable unknown")
    if(any(coms[1] == p.name for p in variables )): Error("Variable name taken")
    variables.append(DataType(coms[1],coms[2],coms[3],len(variables)))
    cache.append([])
    if(debugMode) : print("new Variable : " + coms[1]," has " + coms[2]," and " + coms[3])

def Declare(coms):
    if (len(coms) != 3): Error ("Wrong Declare")
    t = GetType(coms[1])
    if(t == None) : Error("Variable Type Not Found")
    cache[t.index].append(CreateVariable(coms[2],t.index))
    if(debugMode): print ("Sucsessfully Declared Variable")

def CreateVariable(name,type):
    return Variable(name,type,0,0)


#todo mach types
def Assign(coms,f,convert):
    if(len (coms) != 4): Error("NOT 4 COMMANDS WITH ASSIGN")
    v = GetVariable(coms[1],f,convert)
    if v == None: Error("Varialbe to AAssign Not Found")
    
    vL = GetVariable(coms[2],f,convert)
    if vL ==None: Error("ASSIGNING VARIABLE NOT FOUND")

    vR = GetVariable(coms[3],f,convert)
    if vR == None: Error("ASSIGNING VARIABLE NOT FOUND")


    Copy(v,vL,vR)
  
    if debugMode : print("ASSIGNED NEW VARIABLE SUCCESFULL")
def Destroy(coms):
    if(len (coms) != 2): Error("NOT 2 COMMANDS WITH DESTROY")
    v = DeleteVariable(coms[1])
    if v == None: Error("Varialbe to Destroy Not Found")
    
    


    
  
    if debugMode : print("DESTOYED VARIABLE SUCCESFULL")
def Decompose(coms,f,convert):
    if(len (coms) != 4): Error("NOT 4 COMMANDS WITH DECOMPOSE")
    v = GetVariable(coms[1],f,convert)
    if v == None: Error("Varialbe to Decompose Not Found")
    
    vL = GetVariable(coms[2],f,convert)
    if vL ==None: Error("Decompose VARIABLE NOT FOUND")

    vR = GetVariable(coms[3],f,convert)
    if vR == None: Error("Decomposed VARIABLE NOT FOUND")

    vL.origin1 = copy.deepcopy(v.origin1.origin1)
    vL.origin2 = copy.deepcopy(v.origin1.origin2)

    vR.origin1 = copy.deepcopy(v.origin2.origin1)
    vR.origin2 = copy.deepcopy(v.origin2.origin2)
    #DeCopy(v,vL,vR)
  
    if debugMode : print("DECOMPOSE  VARIABLE SUCCESFULL")
def Copy(variable, v1, v2):
    variable.origin1 = copy.deepcopy(v1)
    variable.origin2 = copy.deepcopy(v2)



def AssignBit(coms,f,convert):
    if(len(coms) != 3 ): Error("NOT 3 COMMANDS WITH ASSIGN BIT")
    v = GetVariable(coms[1],f,convert)
    if v == None: 
        Error("NO VARIABLE FOUND TO ASSIGN")
    if v.type !=  0: Error("NOT BIT TO ASSIGNBIT ")
    if coms[2] == "1": v.origin1 = 1
    else : v.origin1 = 0
    if debugMode : print("ASSIGNED NEW VARIABLE SUCCESFULL")
def Flip(coms,f,convert):
    if(len(coms) != 2): Error("Wrong Flip")
    v = GetVariable(coms[1],f,convert)
    if v == None: return
    if v.type !=  0: return
    if v.origin1 == 1: v.origin1 = 0
    else : v.origin1 = 1
def IfOneCheck(coms,f,convert):
    if(len(coms) != 2): Error("IF Wrong")
    c = GetVariable(coms[1],f,convert)
    if(c == None): Error("No Bit Found for If")
    
    global skipNextLine
    if(c.origin1 == 0): skipNextLine =  True
def WhileCheck(coms,f,convert):
    if(len(coms) != 2): Error("While Wrong")
    c = GetVariable(coms[1],f,convert)
    if(c == None): Error("No Bit Found for If")
    
    global skipWhile, whiles,whileNester
    if(c.origin1 == 0): 
        skipWhile =  True
        whileNester = 1
    else : whiles.append(cLine)
def IfCheck(coms,f,convert):
    if(len(coms) != 2): Error("If Wrong")
    c = GetVariable(coms[1],f,convert)
    if(c == None): Error("No Bit Found for If")
    
    global skipIf, ifNester
    if(c.origin1 == 0): 
        skipIf =  True
        ifNester = 1

def EndWhile(coms):
     if(len(coms )!= 1): Error ("Wrong EndWhile")
     l = whiles.pop()
     global cLine 
     cLine = l -1
def DefFunction(coms):
    if(len(coms )% 2 != 0): Error ("Wrong Define Function")
    functions.append(Function(coms[1],cLine,-1))
    global functionMode 
    functionMode = True
    for i in range(1,int((len(coms))/2 )):
        t = GetType(coms[i*2 ])
        if(t == None) : Error("Variable Type Not Found For Function")
        functions[len(functions)-1].parameterStack.append(CreateVariable(coms[i*2 +1],t.index))

    if(debugMode) :print("New Function:"+ coms[1]+ " Creating at "+ str(cLine))
def EndDefFunction(coms):
     if(len(coms )!= 1): Error ("Wrong EndDefine Function")
     f = functions[ len (functions)-1]
     f.end = cLine
     global functionMode 
     functionMode = False
     if(debugMode) :print("New Function:"+ f.name+ " Ends at" + str(cLine))
def PrintSum(coms,f,convert):
    if(len(coms )!= 2): Error ("Wrong PrintSum")
    v = GetVariable(coms[1],f,convert)
    if v == None: Error("No Variable found to Printt")
    global pos 
    pos = -1
    print(GetSum(v))
#CAN ONLY BE USED AT THE START !!!! (no safety net to assure this)
def Include(coms):
    global cLine, content
    if(len(coms )!= 2): Error ("Wrong Include")
    
    lines = content.splitlines()
    del lines[cLine]
    content = "\n".join(lines)
    cLine-= 1
    with open(coms[1], "r") as f:
        
        content =   f.read()  + "\n" + content
    
   
def CheckFunction(coms,f,convert):
    global cLine
    fun = GetFunction(coms[0])
    if(fun == None): Error("LIne not recognized")
    if len(coms) != len (fun.parameterStack)+1 : 
        Error("Funcion not right numbe of parameters")
    stack = []
    for c in coms[1:]:
        v = GetVariable(c,f,convert)
        if(v == None): Error ("Function has Invalid Variable as Input")        
        stack.append(v.name)
    back = cLine 
    cLine = fun.begin -1
       
       
        
    Parse(fun,stack)
    if debugMode: print ("Function ended go back to" + str(back))
    cLine = back
def GetSum(v):
    if(v.type ==  0):
        global pos 
        pos += 1
        if(v.origin1 == 1): 
            return 1*(pow(2,pos))
        else: 
            if v.origin1 == 0: return 0
    return GetSum(v.origin2) + GetSum(v.origin1) 


def Error(message):
    print("")
    print(message)
    print("IN LINE:" +str( cLine))
    quit()

def Parse(f = None,convert = None):
    global skipNextLine ,skipWhile,skipIf,cLine ,whileNester,ifNester,content
    while(cLine < len(content.splitlines())-1):
        cLine += 1
        if(cLine == 401):
            wjpf = None
        line = content.splitlines()[cLine]
        
        if debugMode: print (cLine)
        commands =  line.split(" ")
        if skipNextLine :
            skipNextLine = False
            continue
        if line ==  '': 
          continue
       
        if functionMode:
            if(commands[0] ==  "ENDDEF"): 
                EndDefFunction(commands)
            continue
        if skipWhile:
            if(commands[0] == "WHILE"): whileNester += 1
            if(commands[0] == "ENDWHILE"): whileNester -= 1
            if(whileNester == 0):   skipWhile= False
            continue
        if skipIf:
            if(commands[0] == "IF"): ifNester += 1
            if(commands[0] == "ENDIF"): ifNester -= 1
            if(ifNester == 0):    skipIf = False
            continue

        if(commands[0] == "PRINT"): Print(commands,f,convert)
        elif(commands[0] == "COMBINE"): AddVariable(commands)
        elif(commands[0] == "DECLARE"): Declare(commands)
        elif(commands[0] == "ASSIGN"): Assign(commands,f,convert)
        elif(commands[0] == "DESTROY"): Destroy(commands)
        elif(commands[0] == "DECOMPOSE"): Decompose(commands,f,convert)
        elif(commands[0] == "ASSIGNBIT"): AssignBit(commands,f,convert)
        elif(commands[0] == "FLIP"): Flip(commands,f,convert)
        elif(commands[0] == "PRINTSUM"): PrintSum(commands,f,convert)
        elif(commands[0] == "DEF"): DefFunction(commands)
        elif(commands[0] == "IF"): IfCheck(commands,f,convert)
        elif(commands[0] == "IFONE"): IfOneCheck(commands,f,convert)
        elif(commands[0] == "ENDIF"): None
        elif(commands[0] == "ENDDEF"): return
        elif(commands[0] == "WHILE"): WhileCheck(commands,f,convert)
        elif(commands[0] == "ENDWHILE"): EndWhile(commands)
        elif(commands[0] == "INCLUDE"): Include(commands)
        elif(commands[0] == "#"): None

        else :CheckFunction(commands,f,convert)
       
       



with open("PANS.txt", "r") as file:
    
    content = file.read()
    print("PANS")
    Parse(0)

    

        
