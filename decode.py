''' I / rs, rt / rd
        A / rs, rt / rd
        M / rs, rt / rd
        L / rs / rt ---> rs->rd, rt->rs
        S / rs / rt 
        B / rs, rt / --
''' 
from copy import *

class Decode:
    def __init__(self, map, free, aq, fq, iq, bt, active, bs, fu):
        self.map = map
        self.free = free
        self.aq = aq
        self.fq = fq
        self.iq = iq
        self.bt = bt
        self.active = active
        self.renamed = []
        self.old_physical = []
        self.logical = []
        self.stack = []
        self.bs = bs
        self.fu = fu
        print("Decode unit initialized")

    def rename(self, to_decode):
        decoded, old_physical, logical, stack  = [], [], [], []
        print "\t\t\tBranch stack:", self.bs.bstack
        size = len(to_decode)
        i = 1
        for ins in to_decode:
            ins.rs, ins.rt = self.map.get_mapping(ins.rs), self.map.get_mapping(ins.rt)
            log = ins.rd
            if(ins.type not in ['S', 'B'] and log):
                f = self.free.get_phyreg()
                if(f==-1):
                    print "\t\t\tFree list is empty"
                    break
                self.bt.set_busy(f)
                old_phys = self.map.get_mapping(ins.rd)
                self.map.add_mapping(ins.rd, f)
                ins.rd = f
            else:
                old_phys = -1
                if(ins.type=='B'):
                    if(self.bs.isFull()):
                        undo_fetch = size - i
                        self.fu.instructions = self.fu.store[ins.rd:(ins.rd+undo_fetch+1)] + self.fu.instructions
                        break
                    else:
                        self.bs.Insert(ins, deepcopy(self.map), int(ins.rd))
            i = i+1
            decoded.append(ins)
            old_physical.append(old_phys)
            logical.append(log)
            stack.append(copy(self.bs.bstack))

        self.renamed.extend(decoded)
        self.old_physical.extend(old_physical)
        self.logical.extend(logical)
        self.stack.extend(stack)
        to_issue, old_physical, logical, stack  = [], [], [], []

        f,e,l = 0,0,0
        free_reg = self.free.freeRegisters()
        for i in range(min(self.active.freeSlots(),len(self.renamed),4)):
            ins = self.renamed[i]
            if(ins.type in ['I', 'A', 'M', 'L']):
                if(free_reg==0):
                    break
                free_reg = free_reg-1
            print "\t\t\tChecking instruction for issue: ", ins
            if(ins.type in ['I', 'B']):
                e = e + 1
                if((self.iq.freeSlots()-e)<0):
                    break
            if(ins.type in ['A', 'M']):
                f = f + 1
                if((self.fq.freeSlots()-f)<0):
                    break
            if(ins.type in ['L', 'S']):
                l = l + 1
                if((self.aq.freeSlots()-l)<0):
                    break            
            to_issue.append(ins)
            old_physical.append(self.old_physical[i])
            logical.append(self.logical[i])
            stack.append(self.stack[i])
        i = len(to_issue)
        self.renamed, self.old_physical, self.logical, self.stack = self.renamed[i:], self.old_physical[i:], self.logical[i:], self.stack[i:]
        print "\t\t\tDecode buffer: ", self.renamed
        return (decoded, to_issue, old_physical, logical, stack)
    
    def calc(self, to_decode):
        return self.rename(to_decode)


