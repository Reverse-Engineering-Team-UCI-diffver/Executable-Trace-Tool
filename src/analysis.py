import immlib
from collections import defaultdict


imm = immlib.Debugger()

'''
   initStatsKey()
           Value of the address that is added to the stats dictionary is a list. 
           The list needs to be initialized so that it contains two int that is zero
''' 
def initStatsKey(stats, oldValue):
    stats[oldValue].append(0)
    stats[oldValue].append(0)

'''
   initFuncCount()
           Value of the address that is added to the funcCount dictionary is a list. 
           The list needs to be initialized so that it contains two int that is zero
'''   
def initFuncCount(funcCount, funcAddr):
    funcCount[funcAddr].append(0)
    funcCount[funcAddr].append(0)
 
'''
   statsForAddr()
           Write to the file the statistic for a particular address
'''    
def statsForAddr(statsFile, stats, key):
    #stats is a dictionary. 
    #Key: address. Value: a list with two element. 
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

'''
   writeStatsHeader()
           The header for the file statsFile
'''
def writeStatsHeader(statsFile):
    statsFile.write("Branch Address")
    statsFile.write("\t")
    statsFile.write("Percent True")
    statsFile.write("\t")
    statsFile.write("Percent False")
    statsFile.write("\n")
 
'''
   statfForFunc()
           Write to the file the statistic for a particular address 
'''
def statfForFunc(statfFile, funcCount, key):
    #stats is a dictionary. 
    #Key: address. Value: a list with two element. 
    #First element contains count of how many times user function is called.
    statfFile.write(str(key)) #Address
    statfFile.write("\t\t")
    statfFile.write(str(funcCount[key][0])) #Count
    statfFile.write("\n")

'''
   writeStatfHeader()
           The header for the file statfFile
'''
def writeStatfHeader(statfFile):
    statfFile.write("Function Address")
    statfFile.write("\t")
    statfFile.write("Count")
    statfFile.write("\n")

'''
   findEndAddr()
           Find the end address of program, 'cexit'
'''
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

'''
   findStartAddr()
           Find the start address of main function
'''
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
    imm.run()
    imm.run(startAddr)
    return startAddr

'''
   traceAddr()
           Trace the address line-by-line and search all of branch & CALL instruction
           1. Branch
               Compare current address and next address. 
               Next, set the value whether it is true or false and write file
           2.  CALL
               Find the start address of function and write file
'''
def traceAddr(imm, address, endAddr, stats, oldValue, rawFile, funcFile, funcCount):
    prefixCall = 0
    CBIflag = 0
    stepAddr = 0
    nextAddr = 0
    while(address != endAddr):
        #Finish searching
        if(address == endAddr):
             imm.quitDebugger()

        opcode = imm.disasm(address)
        opcode_str = opcode.getDisasm().lower()
        #If PC points CALL instruction, get the start address of function
        if "call" in opcode_str:
            #Ignore superprefix section
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

        #Ignore JMP instruction
        elif "jmp" in opcode_str:
             address = int(opcode_str.split(".")[1], 16)

        #Searching all control branch instruction
        elif ("cmp" in opcode_str) or ("test" in opcode_str):
             imm.stepOver(endAddr)
             address = imm.getCurrentAddress()
             opcode = imm.disasm(address)
             opcode_str = opcode.getDisasm()
             instruct = opcode_str.split(" ")[0]
            #If PC points to branch instruction, compare current address and next address
             if "J" in instruct:
                  stepAddr = int(opcode_str.split(".")[1], 16)
                  nextAddr = address + opcode.getOpSize()
                  CBIflag = 1
        prevAddr = address
        imm.stepOver(endAddr)
        address = imm.getCurrentAddress()

        #Determine the branch's value whether is true or false
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

'''
    main()

        Step1. Using our function 'findEndAddr()' to search 'cexit' instruction.
        Step2. Using our function 'findStartAddr()' to search the begginning of the main function in executable file and run to start address.
        Step3. Using 'stepOver()' or 'stepIn()' function from start address to find conditional branch and function call instruction.
            - If we find the conditional branch instruction, check and write the value of branch instruction in file which name is 'rawFile'
              and go to next instruction by using the 'stepOver()' function.
            - If we find the function call instruction, count and write ,that how many times of function call, in file which name is 'funcFile'
              and go to next instruction by using the 'stepIn()' function.
            - Iterating this step from start address to end address.
        Step4. Creating the statistics file by using the function 'writeStatsHeader()' and 'writeStatfHeader()'.
        Step5. Closing all files and we create four files 'funcFile', 'rawFile', 'statsFile' and 'statfFile'.

        Note: The 'jmp' instruction is an unconditional jump, so we ignore that instruction in step3.
    
        Key Assumptions:
       
            Superfluous prefix appear just one time ,so all call instructions after that mean function calls.
            'Cmp' or 'test' instructions are always in front of conditional branch instructions.
            The command should be started before run state in immunity debugger.
'''
def main(args):
    
    #Initializing variables 
    
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
    
    #Step 1 -- Find 'cexit' address
    address = findEndAddr(imm, address)
    endAddr = address - 1

    #Step 2 -- Find start address of main
    address = findStartAddr(imm, base, address)

    #Step 3 -- Get the branch execution and function call results
    traceAddr(imm, address, endAddr, stats, oldValue, rawFile, funcFile, funcCount)
    
    #Step 4 -- Create the statistics file
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
