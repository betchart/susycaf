from core.wrappedChain import *
from core import utils
##############################
class deadEcalRegionsFromFile(wrappedChain.calculable) :
    def __init__(self) :
        self.trigPrims = r.std.vector(type(utils.LorentzV()))()
        self.nBadXtals = r.std.vector("int")()
        self.maxStatus = r.std.vector("int")()
        inFile=open("data/deadRegionList.txt")
        for line in inFile :
            if line[0]=="#" : continue
            fieldList = line.split()
            eta  = float(fieldList[0])
            phi  = float(fieldList[1])
            nBad = int(fieldList[4])
            self.trigPrims.push_back(utils.LorentzV(0.0,eta,phi,0.0))
            self.nBadXtals.push_back(nBad)
            self.maxStatus.push_back(14)
        inFile.close()

    def update(self,ignored) :
        self.value={}
        self.value["trigPrims"] = self.trigPrims
        self.value["nBadXtals"] = self.nBadXtals
        self.value["maxStatus"] = self.maxStatus
##############################
class deadHcalChannelsFromFile(wrappedChain.calculable) :
    def __init__(self) :
        self.p4s = r.std.vector(type(utils.LorentzV()))()
        self.status = r.std.vector("int")()
        inFile = open("data/hcalDeadChannels.txt")
        for line in inFile :
            if line[0]=="#" : continue
            fieldList = line.split()
            if not len(fieldList) : continue
            eta    = float(fieldList[0])
            phi    = float(fieldList[1])
            status = int(fieldList[2])
            self.p4s.push_back(utils.LorentzV(0.0, eta, phi, 0.0))
            self.status.push_back(status)
        inFile.close()

    def update(self,ignored) :
        self.value={}
        self.value["p4"] = self.p4s
        self.value["status"] = self.status
##############################
class ecalDeadTowerTrigPrimP4(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "from text file"
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["trigPrims"]
class ecalDeadTowerNBadXtals(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "from text file"
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["nBadXtals"]
class ecalDeadTowerMaxStatus(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to 14"
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadEcalRegionsFromFile"]["maxStatus"]
##############################
class hcalDeadChannelP4(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "from text file"
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadHcalChannelsFromFile"]["p4"]
class hcalDeadChannelStatus(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "from text file"
    def isFake(self) : return True
    def update(self,ignored) : self.value = self.source["deadHcalChannelsFromFile"]["status"]
##############################
class logErrorTooManyClusters(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to False"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class logErrorTooManySeeds(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to False"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
##############################
class beamHaloCSCLooseHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloCSCTightHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"    
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloEcalLooseHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloEcalTightHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloGlobalLooseHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloGlobalTightHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloHcalLooseHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
class beamHaloHcalTightHaloId(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "hard-coded to True"
    def isFake(self) : return True
    def update(self,ignored) : self.value = False
##############################
class isRealData(wrappedChain.calculable) :
    def __init__(self) : self.moreName = "absence of genpthat"
    def update(self,ignored) : self.value = not ("genpthat" in self.source)
##############################
