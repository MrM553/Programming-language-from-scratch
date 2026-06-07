import copy
import time

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
# tells how often per second the time function increments
timeFrames = 60

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

# all information about an active function
class FunctionStack():
    def __init__(self,function,namespace):
        self.function = function
        self.namespace = namespace
variables = [
    DataType("-1",0,0,-1),
    DataType("BIT",0,0,0)]
cache = []
functions  = []

whiles = []
pos = -1


def GetType(name):
    return next ((v for v in variables if(v.name == name)),None)

def GetFunction(name):
     return next ((f for f in functions if(f.name == name)),None)

def GetVariable(name,f):
    var = search_variable(name,f)
    return var
def search_variable(name,f):
    var = None
    if f is not None :
        var = next(
        (cell for cell in f.namespace
         if cell.name == name),
        None
        )
    
    if(var is None): var = next(
        (cell for cell in cache
         if cell.name == name),
        None
    )

    return var

def DeleteVariable(name,f):
    var = GetVariable(name,None)
    if var is not None:
        cache.remove(var)
    var = GetVariable(name,f)
    if var is not None:
        f.namespace.remove(var)
    return var

def Print(coms,f):
    if(len(coms) != 2 ): Error("Print Wrong")
    v = GetVariable(coms[1],f)
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
    if(debugMode) : print("new Variable : " + coms[1]," has " + coms[2]," and " + coms[3])

def Declare(coms,f):
    glob = False
    if len(coms) < 3  : Error ("Wrong Declare")
    if  len(coms) == 4: 
        if coms[3] == "GLOBAL" :  glob = True 
    t = GetType(coms[1])
    if(t == None) : Error("Variable Type Not Found")
    if ( f == None or glob): cache.append(CreateVariable(coms[2],t.index))
    else : f.namespace.append(CreateVariable(coms[2],t.index))
    if(debugMode): print ("Sucsessfully Declared Variable")

def CreateVariable(name,type):
    return Variable(name,type,0,0)


#todo mach types
def Assign(coms,f):
    if(len (coms) != 4): Error("NOT 4 COMMANDS WITH ASSIGN")
    v = GetVariable(coms[1],f)
    if v == None: Error("Varialbe to AAssign Not Found")
    
    vL = GetVariable(coms[2],f)
    if vL ==None: Error("ASSIGNING VARIABLE NOT FOUND")

    vR = GetVariable(coms[3],f)
    if vR == None: Error("ASSIGNING VARIABLE NOT FOUND")


    CopyAssign(v,vL,vR)
  
    if debugMode : print("ASSIGNED NEW VARIABLE SUCCESFULL")
def Destroy(coms,f):
    if(len (coms) != 2): Error("NOT 2 COMMANDS WITH DESTROY")
    v = DeleteVariable(coms[1],f)
    if v == None: Error("Varialbe to Destroy Not Found")
    
    


    
  
    if debugMode : print("DESTOYED VARIABLE SUCCESFULL")
def Decompose(coms,f):
    if(len (coms) != 4): Error("NOT 4 COMMANDS WITH DECOMPOSE")
    v = GetVariable(coms[1],f)
    if v == None: Error("Varialbe to Decompose Not Found")
    
    vL = GetVariable(coms[2],f)
    if vL ==None: Error("Decompose VARIABLE NOT FOUND")

    vR = GetVariable(coms[3],f)
    if vR == None: Error("Decomposed VARIABLE NOT FOUND")

    if  vL.type == -1 : vL.type = v.origin1.type
    if  vR.type == -1 : vR.type = v.origin2.type 

    vL.origin1 = copy.deepcopy(v.origin1.origin1)
    vL.origin2 = copy.deepcopy(v.origin1.origin2)

    vR.origin1 = copy.deepcopy(v.origin2.origin1)
    vR.origin2 = copy.deepcopy(v.origin2.origin2)
    #DeCopy(v,vL,vR)
  
    if debugMode : print("DECOMPOSE  VARIABLE SUCCESFULL")
def CopyAssign(variable, v1, v2):
    variable.origin1 = copy.deepcopy(v1)
    variable.origin2 = copy.deepcopy(v2)


def Copy(variable , toCopy):
    toCopy.origin1 = copy.deepcopy(variable.origin1)
    toCopy.origin2 = copy.deepcopy(variable.origin2)
    if toCopy.type == -1 : toCopy.type = variable.type


def AssignBit(coms,f):
    if(len(coms) != 3 ): Error("NOT 3 COMMANDS WITH ASSIGN BIT")
    v = GetVariable(coms[1],f)
    if v == None: 
        Error("NO VARIABLE FOUND TO ASSIGN")
    if v.type !=  0: 
        Error("NOT BIT TO ASSIGNBIT ")
    if coms[2] == "1": v.origin1 = 1
    else : v.origin1 = 0
    if debugMode : print("ASSIGNED NEW VARIABLE SUCCESFULL")
def Flip(coms,f):
    if(len(coms) != 2): Error("Wrong Flip")
    v = GetVariable(coms[1],f)
    if v == None: return
    if v.type !=  0: return
    if v.origin1 == 1: v.origin1 = 0
    else : v.origin1 = 1
def IfOneCheck(coms,f):
    if(len(coms) != 2): Error("IF Wrong")
    c = GetVariable(coms[1],f)
    if(c == None): Error("No Bit Found for If")
    
    global skipNextLine
    if(c.origin1 == 0): skipNextLine =  True
def WhileCheck(coms,f):
    if(len(coms) != 2): Error("While Wrong")
    c = GetVariable(coms[1],f)
    if(c == None): Error("No Bit Found for If")
    
    global skipWhile, whiles,whileNester
    if(c.origin1 == 0): 
        skipWhile =  True
        whileNester = 1
    else : whiles.append(cLine)
def IfCheck(coms,f):
    if(len(coms) != 2): Error("If Wrong")
    c = GetVariable(coms[1],f)
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
def DefGenFunction(coms):
    if(len(coms )< 2): Error ("Wrong Define Function")
    functions.append(Function(coms[1],cLine,-1))
    global functionMode 
    functionMode = True
    for i in range(2,int((len(coms)) )):
        functions[len(functions)-1].parameterStack.append(CreateVariable(coms[i],-1))

    if(debugMode) :print("New Function:"+ coms[1]+ " Creating at "+ str(cLine))
def EndDefFunction(coms):
     if(len(coms )!= 1): Error ("Wrong EndDefine Function")
     f = functions[ len (functions)-1]
     f.end = cLine
     global functionMode 
     functionMode = False
     if(debugMode) :print("New Function:"+ f.name+ " Ends at" + str(cLine))
def PrintSum(coms,f):
    if(len(coms )!= 2): Error ("Wrong PrintSum")
    v = GetVariable(coms[1],f)
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


def CopyVariable(coms,f):
    if(len(coms) != 3): Error("Wrong Copy Variable")
    v1 =GetVariable(coms[1],f)
    v2 = GetVariable(coms[2],f)
    if v1 is None : Error("Variable1 to Copy not found")
    if v2 is None : Error("Variable2 to Copy not found")
    Copy(v2,v1)

def CheckBit(coms,f):
    if(len(coms) != 3): Error("Wrong IsBit")
    v1 = GetVariable(coms[1],f)
    v2 = GetVariable(coms[2],f)
    if v1.type !=  0 :  Error("Wrong Type for IsBit copy (no BIT)")
    
    if v2.type == 0 : v1.origin1 = 1
    else: v1.origin1 = 0

def CheckFunction(coms,f):
    global cLine
    fun = GetFunction(coms[0])
    funStack = FunctionStack(fun,[])  
    if(fun == None): Error("LIne not recognized")
    if len(coms) != len (fun.parameterStack)+1 : 
        Error("Funcion not right numbe of parameters")
    i = 0
    for c in coms[1:]:
        v = GetVariable(c,f)
        if(v == None): Error ("Function has Invalid Variable as Input")        
        nv = Variable("",-1,0,0)
        Copy(v,nv)
        nv.name = fun.parameterStack[i].name
        i+= 1
        funStack.namespace.append(nv)

    back = cLine 
    cLine = fun.begin -1
       
    Parse(funStack)
    i = len(coms)-1
    while i >= 1:
        v = GetVariable(coms[i],f)
        nv = funStack.namespace[i-1]
        i-= 1      
        Copy(nv,v)
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
def GetTime(coms,f):
    if(len(coms) != 2): Error("Wrong Time")
    v = GetVariable(coms[1],f)
    if v == None: Error("No Variable found to Printt")

    global launchtime, timeFrames
    assignTime =  time.time() - launchtime
    assignTime = int(assignTime * timeFrames)
    global pos
    pos = -1
    AssignTime(v,assignTime)
def AssignTime(v,time):
    global pos
    if v.type == 0:
        pos += 1
        v.origin1 = (time >> pos) & 1
    
       
    else:
        AssignTime(v.origin2,time)
        AssignTime(v.origin1,time)
def Error(message):
    print("")
    print(message)
    print("IN LINE:" +str( cLine))
    quit()

def Parse(f):
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

        if(commands[0] == "PRINT"): Print(commands,f)
        elif(commands[0] == "COMBINE"): AddVariable(commands)
        elif(commands[0] == "DECLARE"): Declare(commands,f)
        elif(commands[0] == "ASSIGN"): Assign(commands,f)
        elif(commands[0] == "DESTROY"): Destroy(commands,f)
        elif(commands[0] == "DECOMPOSE"): Decompose(commands,f)
        elif(commands[0] == "ASSIGNBIT"): AssignBit(commands,f)
        elif(commands[0] == "FLIP"): Flip(commands,f)
        elif(commands[0] == "PRINTSUM"): PrintSum(commands,f)
        elif(commands[0] == "DEF"): DefFunction(commands)
        elif(commands[0] == "DEFGEN"): DefGenFunction(commands)
        elif(commands[0] == "IF"): IfCheck(commands,f)
        elif(commands[0] == "IFONE"): IfOneCheck(commands,f)
        elif(commands[0] == "ENDIF"): None
        elif(commands[0] == "ENDDEF"): return
        elif(commands[0] == "WHILE"): WhileCheck(commands,f)
        elif(commands[0] == "ENDWHILE"): EndWhile(commands)
        elif(commands[0] == "INCLUDE"): Include(commands)
        elif(commands[0] == "COPY"): CopyVariable(commands,f)
        elif(commands[0] == "ISBIT"): CheckBit(commands,f)
        elif(commands[0] == "#"): None
        elif(commands[0] == "TIME" ): GetTime(commands,f)

        else :CheckFunction(commands,f)
       
       



with open("PANS.txt", "r") as file:
    global launchtime
    launchtime = time.time()
    content = file.read()
    print("PANS")
    Parse(0)

    

        
