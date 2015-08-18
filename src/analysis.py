import immlib
from collections import defaultdict

imm = immlib.Debugger()

#
#   initStatsKey
#           Value of the address that is added to the stats dictionary is a list. 
#           The list needs to be initialized so that it contains two int that is zero
# 
def initStatsKey(stats, oldValue):
    stats[oldValue].append(0)
    stats[oldValue].append(0)

#
#   initFuncCount
#           Value of the address that is added to the funcCount dictionary is a list. 
#           The list needs to be initialized so that it contains two int that is zero
#   
def initFuncCount(funcCount, funcAddr):
    funcCount[funcAddr].append(0)
    funcCount[funcAddr].append(0)
 
#
#   statsForAddr
#           Write to the file the statistic for a particular address
#    
def statsForAddr(statsFile, stats, key):
    #stats is a dictionary. Key: address. Value: a list with two element. 
    #First element contains amount of time it is true.
    #Second element contains amount of time it is false.
    statsFile.write(str(key)) #Address
    statsFile.write("\t\t")
    trueP = str((float(stats[key][0])/(stats[key][0]+stats[key][1]))*100)
    statsFile.write(trueP.split(".")[0]+"."+trueP.split(".")[1][0]) #Percentage of times it is true
    statsFile.write("\t\t")
    falseP = str((float(stats[key][1])/(stats[key][0]+stats[key][1]))*100)
    statsFile.write(falseP.split(".")[0]+"."+falseP.split(".")[1][0])#Percentage of times it is false
    statsFile.write("\n")

#
#   writeStatsHeader
#           The header for the file statsFile
#
def writeStatsHeader(statsFile):
    statsFile.write("Branch Address")
    statsFile.write("\t")
    statsFile.write("Percent True")
    statsFile.write("\t")
    statsFile.write("Percent False")
    statsFile.write("\n")
 
#
#   statfForFunc
#           Write to the file the statistic for a particular address
#
def statfForFunc(statfFile, funcCount, key):
    #stats is a dictionary. Key: address. Value: a list with two element. First element contains amount of
    statfFile.write(str(key)) #Address
    statfFile.write("\t\t")
    statfFile.write(str(funcCount[key][0])) #Count
    statfFile.write("\n")

#
#   writeStatfHeader
#           The header for the file statfFile
#
def writeStatfHeader(statfFile):
    statfFile.write("Function Address")
    statfFile.write("\t")
    statfFile.write("Count")
    statfFile.write("\n")

#
#   findEndAddr
#           Find the end address of program, 'cexit'
#
def findEndAddr(imm, address):
    while(1) :
        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()

        if "cexit" in opcode_str:
            endAddr = address
            address -= 1
            break
        else :
            address += opcode.getOpSize()
    return address

#
#   findStartAddr
#           Find the start address of main function
#
def findStartAddr(imm, base, address):
    while(address > base):
        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()

        if "call" in opcode_str:
            #callmain = address
            startAddr = int(opcode_str.split(".")[1], 16)
            break
        else:
            address -= 1
    address = imm.getCurrentAddress()
    if(address > 0x0040FFFF):
        imm.run()
    imm.run(startAddr)
    return startAddr

#
#   traceAddr
#           trace the address line-by-line and search all of branch & CALL instruction
#           1. branch
#               compare current address and next address. 
#               next, set the value whether it is true or false and write file
#           2.  CALL
#               find the start address of function and write file
#
def traceAddr(imm, address, endAddr, stats, oldValue, rawFile, funcFile, funcCount):
    prefixCall = 0
    CBIflag = 0
    stepAddr = 0
    nextAddr = 0
    while(address != endAddr):
        #finish searching
        if(address == endAddr):
             imm.quitDebugger()

        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()
        #if PC points CALL instruction, get the start address of function
        if "call" in opcode_str:
            #ignore superprefix section
            if(prefixCall == 0):
                name = opcode_str.split(".")[0].lower()
                prefixCall = 1
            elif name in opcode_str:
                calledAddr = opcode_str.split(".")[1].upper()
                funcFile.write(calledAddr)
                funcFile.write("\n")
                if calledAddr not in funcCount:
                    initFuncCount(funcCount, calledAddr)
                funcCount[calledAddr][0]+=1
                imm.stepIn(endAddr)
                address = imm.getCurrentAddress()

        #ignore JMP instruction
        elif "jmp" in opcode_str:
             address = int(opcode_str.split(".")[1], 16)

        #branch instruction search part
        elif ("cmp" in opcode_str) or ("test" in opcode_str):
             imm.stepOver(endAddr)
             address = imm.getCurrentAddress()
             opcode = imm.disasm(address)
             opcode_str = opcode.getDisasm()
             instruct = opcode_str.split(" ")[0]
            #if PC points branch instruction, check current address and next address
             if "J" in instruct:
                  stepAddr = int(opcode_str.split(".")[1], 16)
                  nextAddr = address + opcode.getOpSize()
                  CBIflag = 1
        prevAddr = address
        imm.stepOver(endAddr)
        address = imm.getCurrentAddress()

        #determine the branch has true or false
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


def main(args):
    #variable initialize
    
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
    name=imm.getDebuggedName()
    module=imm.getModule(name)
    address=module.getBaseAddress()
    base = address
    
    #Step 1  -- find 'cexit' address
    address = findEndAddr(imm, address)
    endAddr = address - 1

    #Step 2 -- find start address of main
    address = findStartAddr(imm, base, address)

    #Step 3 -- get the branch execution and function call results
    traceAddr(imm, address, endAddr, stats, oldValue, rawFile, funcFile, funcCount)
    
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
