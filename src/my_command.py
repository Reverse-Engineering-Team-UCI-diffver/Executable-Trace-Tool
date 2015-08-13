import immlib

def main(args):
    imm = immlib.Debugger()
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
        
        if "call" in opcode_str:
            if(prefixCall == 0):
                prefixCall = 1
            elif name in opcode_str:
                calledAddr = opcode_str.split(".")[1].upper()
                imm.log(hex(address).upper() + "   This is call instruction jump to " + calledAddr)
                imm.stepIn(endAddr)
                address = imm.getCurrentAddress()
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
             if(address == stepAddr):
                  imm.log(hex(prevAddr).upper() + "   Conditional branch is True!!!")
             elif(address == nextAddr):
                  imm.log(hex(prevAddr).upper() + "   Conditional branch is False!!!")
    
    return "Search completed!"
