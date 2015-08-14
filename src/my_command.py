import immlib
from collections import defaultdict

imm = immlib.Debugger()

# if a process has spaces, capital letters, or is over 8 characters long it needs to be modified
# for example, the process "Hello World.exe" appears as "hello_wo" in the assembly code


def initStatsKey(stats, oldValue):
    '''Value of the address that is added to the stats dictionary is a list. The list needs to be initialized
    so that it contains two int that is zero'''
    stats[oldValue].append(0)
    stats[oldValue].append(0)
   
def initFuncCount(funcCount, funcAddr):
    '''Value of the address that is added to the funcCount dictionary is a list. The list needs to be initialized
    so that it contains two int that is zero'''
    funcCount[funcAddr].append(0)
    funcCount[funcAddr].append(0)
        
def statsForAddr(statsFile, stats, key):
    '''Write to the file the statistic for a particular address'''
    #stats is a dictionary. Key: address. Value: a list with two element. First element contains amount of
    #time it is true. Second element contains amount of time it is false.
    statsFile.write(hex(long(key))) #Address
    statsFile.write("\t\t")
    trueP = str((float(stats[key][0])/(stats[key][0]+stats[key][1]))*100)
    statsFile.write(trueP.split(".")[0]+"."+trueP.split(".")[1][0]) #Percentage of times it is true
    statsFile.write("\t\t")
    falseP = str((float(stats[key][1])/(stats[key][0]+stats[key][1]))*100)
    statsFile.write(falseP.split(".")[0]+"."+falseP.split(".")[1][0])#Percentage of times it is false
    statsFile.write("\n")

def writeStatsHeader(statsFile):
    '''The header for the file statsFile'''
    statsFile.write("Breakpoint Address")
    statsFile.write("\t")
    statsFile.write("Percent True")
    statsFile.write("\t")
    statsFile.write("Percent False")
    statsFile.write("\n")
 
def statsForFunc(statfFile, funcCount, key):
    '''Write to the file the statistic for a particular address'''
    #stats is a dictionary. Key: address. Value: a list with two element. First element contains amount of
    statfFile.write(hex(long(key))) #Address
    statfFile.write("\t\t")
    statfFile.write(funcCount[key][0]) #Count
    statsFile.write("\n")

def writeStatfHeader(statfFile):
    '''The header for the file statfFile'''
    statsFile.write("Function Address")
    statsFile.write("\t")
    statsFile.write("Count")
    statsFile.write("\n")

def main(args):
    # rawFile =  controlbranch addr : boolean
	# funcFile = functionaddr
	# statsFile = percentage of true at each control branch
	# statfFile = count how many times local function is called
    rawFile = open('data.txt', 'a')
    funcFile = open('func.txt', 'a')
    statsFile = open('stats.txt', 'a')
    statfFile = open('statf.txt', 'a')
    
    files = [rawFile, funcFile, statsFile, statfFile]

    oldValue = ""
    funcAddr = ""
    stats = defaultdict(list)
    funcCount = defaultdict(list)

    # this code block finds the last address in the entire executable. We use it in our while loop to make sure we don't run off the end of the program
    name=imm.getDebuggedName()
    module=imm.getModule(name)
    name = name.split(".")[0]
    address=module.getBaseAddress()
    base = address
    mod_size=module.getCodesize()
    last_address = address+mod_size

    while(address < last_address) :
        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()

        if "cexit" in opcode_str:
            endAddr = address
            address -= 1
            break
        else :
            address += opcode.getOpSize()


    while(address > base):
        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()

        if "call" in opcode_str:
            callmain = address
            startAddr = int(opcode_str.split(".")[1], 16)
            break
        else:
            address -= 1
    address = imm.getCurrentAddress()
    if(address > 0x0040FFFF):
        imm.run()
    imm.run(startAddr)
    address = startAddr
    prefixCall = 0
    CBIflag = 0

    while(address != endAddr):
        if(address == endAddr):
             imm.quitDebugger()

        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()
        #if "call" in opcode_str:
        #   funcAddr=opcode_str.split(".")[1].upper()
        #   initFuncCount(funcCount, funcAddr)
        if "call" in opcode_str:
            if(prefixCall == 0):
                prefixCall = 1
            elif name in opcode_str:
                calledAddr = opcode_str.split(".")[1].upper()
                #imm.log(hex(address).upper() + "   This is call instruction jump to " + calledAddr)
                funcFile.write(calledAddr)
                funcFile.write("\n")
                funcCount[calledAddr][0]+=1
                imm.stepIn(endAddr)
                address = imm.getCurrentAddress()
            else:
                imm.stepOver(endAddr)
        elif "jmp" in opcode_str:
             address = int(opcode_str.split(".")[1], 16)
        elif ("cmp" in opcode_str) or ("test" in opcode_str):
             imm.stepOver(endAddr)
             address = imm.getCurrentAddress()
             opcode = imm.disasm(address)
             opcode_str = opcode.getDisasm()
             instruct = opcode_str.split(" ")[0]
        
             if "J" in instruct:
                  stepAddr = int(opcode_str.split(".")[1], 16)
                  nextAddr = address + opcode.getOpSize()
                  CBIflag = 1


        prevAddr = address
        imm.stepOver(endAddr)
        address = imm.getCurrentAddress()

        if(CBIflag):
             CBIflag = 0
             oldValue=hex(prevAddr).upper()
             initStatsKey(stats, oldValue)

             if(address == stepAddr):
                 rawFile.write(hex(prevAddr).upper()+":True \n")
                 stats[oldValue][0]+=1
             elif(address == nextAddr):
                 rawFile.write(hex(prevAddr).upper()+":False \n")
                 stats[oldValue][1]+=1
    
    #Write to the statsFile
    writeStatsHeader(statsFile)
    writeStatfHeader(statfFile)

    for key in stats:
        statsForAddr(statsFile, stats, key)
    for key in funcCount:
        statfForFunc(statfFile, funcCount, key)
    #Close all files
    for f in files:
        f.close()
        
    return "Search completed!"
