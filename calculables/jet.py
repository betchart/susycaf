import math,bisect,itertools,ROOT as r
from supy import wrappedChain,calculables,utils
try:
    import numpy as np
except:
    pass

def xcStrip(collection) :
    return (collection[0].lstrip("xc"),collection[1])
##############################
class IndicesModified(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","CorrectedP4"])
        self.treeP4 = self.CorrectedP4[2:]
        self.moreName = "%s differs from %s"%(self.treeP4,self.CorrectedP4)
    def differentP4(self,i) : return self.source[self.treeP4][i] != self.source[self.CorrectedP4][i]
    def update(self,ignored) :
        self.value = filter(self.differentP4, self.source[self.Indices])
##############################
class IndicesKilled(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
    def update(self,ignored) : self.value = set()
##############################
class IndicesOther(calculables.IndicesOther) :
    def __init__(self, collection = None) :
        super(IndicesOther, self).__init__(collection)
        self.moreName = "pass ptMin; fail jetID or etaMax"
##############################
class HtBinContainer(wrappedChain.calculable) :
    """this is hacky-- see Indices and HtBin"""
    def __init__(self, collection = None) :
        self.fixes = collection
        self.indices = "%sIndices%s"%collection
        self.htBinContainer = "%sHtBinContainer%s"%collection

    def update(self,ignored) : #copied from calculables.indicesOther
        self.value = []
        if not self.source.node(self.indices).updated :
            self.source[self.indices]
##############################
class HtBin(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["HtBinContainer"])

    def update(self,ignored) :
        l = self.source[self.HtBinContainer]
        self.value = l[0] if len(l) else None
##############################
class Indices(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, etaMax = None, flagName = None, extraName = "",
                 scaleThresholds = False, htBins = None, referenceThresholds = None):
        self.fixes = (collection[0],collection[1]+extraName)
        self.stash(["IndicesOther"])
        self.stash(["CorrectedP4", "IndicesKilled"],collection)
        self.flag = None if not flagName else \
                    ( "%s"+flagName+"%s" if xcStrip(collection)[0][-2:] != "PF" else \
                      "%sPF"+flagName+"%s" ) % xcStrip(collection)
        for item in ["extraName", "etaMax", "scaleThresholds", "htBins", "referenceThresholds"] :
            setattr(self, item, eval(item))
        if not self.scaleThresholds :
            self.pt2Min = ptMin*ptMin
            self.moreName = "pT>=%.1f GeV; |eta|<%.1f; %s"% (ptMin, etaMax, flagName if flagName else "")
        else :
            self.stash(["HtBinContainer"])
            self.moreName = "|eta|<%.1f; %s; %s; %s"% (etaMax, flagName if flagName else "", str(self.referenceThresholds), str(self.htBins))

    def update(self, ignored) :
        if not self.scaleThresholds :
            self.updateSimple()
        else :
            self.updateWithScaling()

    def jetLoop(self, p4s, killed, ids, ptMin) :
        pts = []
        indices = []
        others = []
        ht = 0.0
        for i in range(p4s.size()) :
            pt = p4s.at(i).pt()
            et = p4s.at(i).Et()
            pts.append(pt)
            if pt < ptMin or i in killed: continue
            elif ids[i] and abs(p4s.at(i).eta()) < self.etaMax :
                ht+=et
                indices.append(i)
            else: others.append(i)
        indices.sort( key = pts.__getitem__, reverse = True)
        return ht,indices,others

    def finish(self, indices, others, htThreshold, other, htBinContainer) :
        self.value = indices
        for iOther in others :
            other.append(iOther)
        htBinContainer.append(htThreshold)
        #print "%sIndices%s"%self.fixes,"=",self.source["%sIndices%s"%self.fixes]
        #print "%sIndicesOther%s"%self.fixes,"=",self.source["%sIndicesOther%s"%self.fixes]
        
    def updateWithScaling(self) :
        self.value = []
        p4s    = self.source[self.CorrectedP4]
        htBinContainer = self.source[self.HtBinContainer] if not self.extraName else None
        other  = self.source[self.IndicesOther] if not self.extraName else []
        killed = self.source[self.IndicesKilled]
        jetIds = self.source[self.flag] if self.flag else p4s.size()*[1]

        #print
        #print " entry    ptMin  htThresh       ht                indices                 others"
        #print "--------------------------------------------------------------------------------"
        for htThreshold in reversed(self.htBins) :
            ptMin = self.referenceThresholds["singleJetPt"]*htThreshold/self.referenceThresholds["ht"]
            ht,indices,others = self.jetLoop(p4s, killed, jetIds, ptMin)
            #print "%6d     %4.1f    %6.1f   %6.1f   %20s   %20s"%(self.source["entry"], ptMin, htThreshold, ht, str(indices), str(others))
            if ht>htThreshold :
                self.finish(indices, others, htThreshold, other, htBinContainer)
                return
        #did not make it into any HT bin; use the last values
        self.finish(indices, others, None, other, htBinContainer)
            
    def updateSimple(self) :
        self.value = []
        p4s    = self.source[self.CorrectedP4]
        other  = self.source[self.IndicesOther] if not self.extraName else []
        killed = self.source[self.IndicesKilled]
        jetIds = self.source[self.flag] if self.flag else p4s.size()*[1]
        pt2s    = []

        for i in range(p4s.size()) :
            pt2 = p4s.at(i).Perp2()
            pt2s.append(pt2)
            if pt2 < self.pt2Min or i in killed: continue
            elif jetIds[i] and abs(p4s.at(i).eta()) < self.etaMax :
                self.value.append(i)
            else: other.append(i)
        self.value.sort( key = pt2s.__getitem__, reverse = True)
####################################
class IndicesPhi(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices"])
    def update(self,ignored) :
        self.value = utils.phiOrder(self.source[self.CorrectedP4], self.source[self.Indices])
####################################
class IndicesIgnored(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices","IndicesOther"])
        self.moreName = "jets not in Indices, IndicesOther"
    def update(self,ignored) :
        self.value = list(set(range(len(self.source[self.CorrectedP4]))) - set(self.source[self.Indices]) - set(self.source[self.IndicesOther]))
###################################
class IndicesBtagged(wrappedChain.calculable) :
    '''
    CMS PAS BTV-09-001
    CMS PAS BTV-10-001
    '''
    def __init__(self,collection,tag) :
        self.fixes = collection
        self.stash(["Indices"])
        self.tag = ("%s"+tag+"%s") % xcStrip(collection)
        self.moreName = "Ordered by %s; %s%s"%((tag,)+collection)
    def update(self,ignored) :
        self.value = sorted(self.source[self.Indices],
                            key = self.source[self.tag].__getitem__, reverse = True )
###################################
class IndicesGenB(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["Indices","CorrectedP4"])
    
    def matchesGenB(self,index) :
        genP4s = self.source["genP4"]
        p4s = self.source[self.CorrectedP4]
        for iGenB in self.source["genIndicesB"] :
            bP4 = genP4s[iGenB]
            p4 = p4s[index]
            if r.Math.VectorUtil.DeltaR(p4,bP4) < 0.6 : return True #and abs(p4.pt()-bP4.pt()) / bP4.pt() < 0.4 : return True
        return False
    def update(self,ignored) : self.value = filter(self.matchesGenB, self.source[self.Indices])
###################################
class IndicesGenWqq(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["Indices","CorrectedP4"])
    
    def matchesGenWqq(self,index) :
        genP4s = self.source["genP4"]
        p4s = self.source[self.CorrectedP4]
        for iGenQ in self.source["genIndicesWqq"] :
            qP4 = genP4s[iGenQ]
            p4 = p4s[index]
            if r.Math.VectorUtil.DeltaR(p4,qP4) < 0.5 and abs(p4.pt()-qP4.pt()) / qP4.pt() < 0.4 : return True
        return False
    def update(self,ignored) : self.value = filter(self.matchesGenWqq, self.source[self.Indices])
###################################
class NMuonsMatched(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4"])
        self.multiplicity = "%sCorrectedP4%s"%xcStrip(collection)
    def update(self,ignored) :
        self.value = [0] * len(self.source[self.multiplicity])
        if not self.source.node(self.CorrectedP4).updated :
            self.source[self.CorrectedP4] #xc modifies values
###################################
class Nmuon(wrappedChain.calculable) :
    '''Leaf for PF, calculable list of 0s for Calo.'''
    def __init__(self, collection = None) :
        self.fixes = xcStrip(collection)
        self.stash(["CorrectedP4"])
    def update(self,ignored) :
        self.value = [0] * len(self.source[self.CorrectedP4])
###################################
class PFJetID(wrappedChain.calculable) :
    # following http://indico.cern.ch/getFile.py/access?contribId=0&resId=0&materialId=slides&confId=97994
    def __init__(self, collection = None, level = None) :
        self.fixes = xcStrip(collection)
        self.stash(["CorrectedP4","FneutralHad","FneutralEm","FchargedHad","FchargedEm","Ncharged","Nneutral"])

        i = ["loose","medium","tight"].index(level)
        self.fNhMax   = [0.99, 0.95, 0.90][i]
        self.fNeMax   = [0.99, 0.95, 0.90][i]
        self.nMin     = [2,    2,    2   ][i]
        self.etaDiv       = 2.4
        self.fChMin   = [0.0,  0.0,  0.0 ][i]
        self.fCeMax   = [0.99, 0.99, 0.99][i] 
        self.nCMin    = [1,    1,    1   ][i]     

        self.moreName = "fN_had<%.2f; fN_em<%.2f; nC+nN>=%d;"% \
                        ( self.fNhMax, self.fNeMax, self.nMin) 
        self.moreName2 = "|eta|>2.4 or {fC_had>%.2f; fC_em <%.2f; nC>%d}" % \
                         (self.fChMin, self.fCeMax, self.nCMin )

    def update(self,ignored) :
        self.value = map(self.passId, 
                         self.source[self.CorrectedP4],
                         self.source[self.FneutralHad],
                         self.source[self.FneutralEm],
                         self.source[self.FchargedHad],
                         self.source[self.FchargedEm],
                         self.source[self.Nneutral],
                         self.source[self.Ncharged] )

    def passId(self, p4, fNh, fNe, fCh, fCe, nN, nC ) :
        return fNh    < self.fNhMax and \
               fNe    < self.fNeMax and \
               nN+nC >= self.nMin   and \
               ( abs(p4.eta()) > self.etaDiv or \
                 fCh > self.fChMin  and \
                 fCe < self.fCeMax  and \
                 nC >= self.nCMin )
class PFJetIDloose(PFJetID) :
    def __init__(self, collection = None) :
        super(PFJetIDloose,self).__init__(collection,"loose")
class PFJetIDmedium(PFJetID) :
    def __init__(self, collection = None) :
        super(PFJetIDmedium,self).__init__(collection,"medium")
class PFJetIDtight(PFJetID) :
    def __init__(self, collection = None) :
        super(PFJetIDtight,self).__init__(collection,"tight")
#############################
class LeadingPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices"])
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        indices = self.source[self.Indices]
        self.value = p4s.at(indices[0]).pt() if len(indices) else None
##############################
class Pt(wrappedChain.calculable) :
    def __init__(self,collection=None) :
        self.fixes = collection
        self.stash(["CorrectedP4"])
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        self.value = [p4s.at(i).pt() for i in range(len(p4s))]
##############################
class SumPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Pt","Indices"])
    def update(self,ignored) :
        pts = self.source[self.Pt]
        self.value = reduce( lambda x,i: x+pts[i], self.source[self.Indices] , 0)
##############################
class RawSumPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4"],xcStrip(collection))
    def update(self,ignored) :
        #self.value = sum([p4.pt() for p4 in self.source[self.CorrectedP4]])
        self.value = sum(utils.hackMap(lambda p4: p4.pt(), self.source[self.CorrectedP4]))
##############################
class SumPz(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices"])
    def update(self,ignored) :
        p4s = self.CorrectedP4()
        self.value = reduce( lambda x,i: x+abs(p4s.at(i).pz()), self.source[self.Indices], 0)
##############################
class SumEt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices"])
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        self.value = reduce( lambda x,i: x+p4s.at(i).Et(), self.source[self.Indices] , 0)
##############################
class SumP4(wrappedChain.calculable) :
    def __init__(self, collection = None, extraName = "") :
        self.fixes = (collection[0],collection[1]+extraName)
        self.stash(["Indices"])
        self.stash(['CorrectedP4'],collection)
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        indices = self.source[self.Indices]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices, utils.LorentzV()) if len(indices) else None
####################################
class SumP4Ignored(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["CorrectedP4","IndicesIgnored"])
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        self.value = reduce( lambda x,i: x+p4s.at(i), self.source[self.IndicesIgnored], utils.LorentzV())
#####################################
class RawSumP4(wrappedChain.calculable) :
    def __init__(self, collection) :
        self.fixes = collection
        self.stash(['CorrectedP4'],xcStrip(collection))
        self.value = utils.LorentzV()
    def update(self,ignored) : 
        self.value.SetCoordinates(0,0,0,0)
        #self.value = sum(self.source[self.CorrectedP4],self.value)
        p4s = self.source[self.CorrectedP4]
        for i in range(len(p4s)) : self.value += p4s[i]
####################################
class Mht(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["SumP4"])
    def update(self,ignored) :
        SumP4 = self.source[self.SumP4]
        self.value = SumP4.pt() if SumP4 else None
####################################
class MhtIgnored(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["SumP4Ignored"])
    def update(self,ignored) :
        self.value = self.source[self.SumP4Ignored].pt()
####################################
class Meff(wrappedChain.calculable) :
    def __init__(self, collection, etRatherThanPt = None) :
        self.fixes = (collection[0], ("Et" if etRatherThanPt else "Pt") + collection[1])        
        self.stash(["Mht"], collection)
        self.stash(["Sum"])
    def update(self,ignored) :
        self.value = self.source[self.Mht]+self.source[self.Sum]
##############################
class M3(wrappedChain.calculable) :
    def __init__(self, collection) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices"])
    def update(self,ignored) :
        p4 = self.source[self.CorrectedP4]
        sumP4s = sorted([p4[i]+p4[j]+p4[k] for i,j,k in itertools.combinations(self.source[self.Indices], 3)], key = lambda sumP4 : -sumP4.pt() )
        self.value = sumP4s[0].M() if sumP4s else None
####################################
class Boost(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["SumP4"])
    def update(self,ignored) :
        self.value = self.sources[self.SumP4].pz()
####################################
class RelativeBoost(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["Boost","SumPz"])
    def update(self,ignored) :
        self.value = self.source[self.Boost] / self.source[self.SumPz]
##############################
class LongP4(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4","Indices"])
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        self.value = reduce(lambda x,p4: max(x+p4,x-p4,key=lambda p:p.pt()), [p4s.at(i) for i in self.source[self.Indices]], utils.LorentzV())
##############################
class Stretch(wrappedChain.calculable) :
    def __init__(self,collection=None) :
        self.fixes = collection
        self.stash(["LongP4","SumPt"])
    def update(self,ignored) :
        self.value = self.source[self.LongP4].pt() / self.source[self.SumPt]
##############################
class CosLongMht(wrappedChain.calculable) :
    def __init__(self,collection=None) :
        self.fixes = collection
        self.stash(["SumP4","LongP4"])
    def update(self,ignored) :
        self.value = abs(math.cos(r.Math.VectorUtil.DeltaPhi(self.source[self.SumP4],self.source[self.LongP4])))
##############################
class PartialSumP4(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["CorrectedP4","IndicesPhi"])
    def update(self,ignored) :
        self.value = utils.partialSumP4( self.source[self.CorrectedP4], self.source[self.IndicesPhi])
class PartialSumP4Centroid(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["PartialSumP4"])
    def update(self,ignored) :
        self.value = utils.partialSumP4Centroid(self.source[self.PartialSumP4])
class PartialSumP4Area(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["PartialSumP4"])
    def update(self,ignored) :
        self.value = utils.partialSumP4Area(self.source[self.PartialSumP4])
class Pi(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["PartialSumP4Area"])
        self.stash(["Meff"], (collection[0], "Pt"+collection[1]))
    def update(self,ignored) :
        self.value = 0.25 * self.source[self.Meff]**2 / self.source[self.PartialSumP4Area]
##############################
class SumP4PlusPhotons(wrappedChain.calculable) :
    def __init__(self, collection = None, extraName = "", photon = None) :
        self.fixes = (collection[0],collection[1]+extraName)
        self.stash(["Indices"])
        self.stash(["CorrectedP4"],collection)
        self.photonP4 = '%sP4%s' % photon
        self.photonIndices = '%sIndices%s' % photon
        
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        indices = self.source[self.Indices]
        self.value = reduce( lambda x,i: x+p4s.at(i), indices[1:], p4s.at(indices[0]) ) if len(indices) else None
        for i in self.source[self.photonIndices] :
            self.value += self.source[self.photonP4].at(i)
##############################
class DeltaPseudoJet(wrappedChain.calculable) :
    def __init__(self, collection = None, etRatherThanPt = None) :
        self.fixes = (collection[0], ("Et" if etRatherThanPt else "Pt") + collection[1])
        self.stash(["CorrectedP4","Indices"],collection)
        self.etRatherThanPt = etRatherThanPt

    def update(self,ignored) :
        indices = self.source[self.Indices]
        p4s = self.source[self.CorrectedP4]
        if not len(indices) :
            self.value = 0.0
            return
        
        diff = [0.] * (1<<(len(indices)-1))
        for iJet,j in enumerate(indices) :
            pt = p4s.at(j).pt() if not self.etRatherThanPt else p4s.at(j).Et()
            for i in range( len(diff) ) :
                diff[i] += pt * (1|-(1&(i>>iJet)))
        
        self.value = min([abs(d) for d in diff])
##############################
class DeltaHtOverHt(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["DeltaPseudoJetEt","SumEt"])
    def update(self,ignored) :
        self.value = self.source[self.DeltaPseudoJetEt]/self.source[self.SumEt]
##############################
class MhtOverHt(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["Mht","SumEt"])
    def update(self,ignored) :
        mht = self.source[self.Mht]
        ht = self.source[self.SumEt]
        self.value = mht/ht if (ht!=None and mht!=None) else None
##############################
class AlphaT(wrappedChain.calculable) :
    def __init__(self, collection = None, etRatherThanPt = None) :
        self.fixes = (collection[0], ("Et" if etRatherThanPt else "Pt") + collection[1])
        self.stash(["Sum","DeltaPseudoJet"])
        self.stash(["SumP4"], collection)
    def update(self,ignored) :
        sumP4   = self.source[self.SumP4]
        ht = self.source[self.Sum]
        self.value = 0.5 * ( ht - self.source[self.DeltaPseudoJet] ) / math.sqrt( ht*ht - sumP4.Perp2() ) if sumP4 else 0
##############################
class AlphaTCpp(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = (collection[0], "Et"+ collection[1])
        self.stash(["Sum"])
        self.stash(["CorrectedP4", "Indices", "SumP4"], collection)
    def update(self,ignored) :
        ETs = r.std.vector("double")()
        for iJet in self.source[self.Indices] :
            ETs.push_back(self.source[self.CorrectedP4].at(iJet).Et())
        self.value = r.alphaT(self.source[self.Sum], r.deltaHt(ETs), self.source[self.SumP4].pt())
##############################
class AlphaTWithPhoton1PtRatherThanMht(wrappedChain.calculable) :
    @property
    def name(self) : return "%sAlphaTWithPhoton1PtRatherThanMht%s" % self.cs

    def __init__(self, collection = None, photons = None, photonIndices = None, etRatherThanPt = None) :
        self.cs = collection
        self.fixes = (collection[0], ("Et" if etRatherThanPt else "Pt") + collection[1])
        self.stash(["Sum","DeltaPseudoJet"])
        self.stash(["SumP4"],collection)
        self.stash(["Indices","P4"],photons)
        
        self.moreName = "some exception"
        
    def update(self,ignored) :
        indices = self.source[self.Indices]
        if not indices :
            self.value = None
            return
        ht = self.source[self.Sum]
        ht2 = ht*ht
        mht2 = self.source[self.P4].at(indices[0]).Perp2()
        mht2Use = mht2 if mht2<ht2 else 0.99*ht2
        self.value = 0.5 * ( ht - self.source[self.DeltaPseudoJet] ) / math.sqrt( ht*ht - mht2Use ) 
##############################
class AlphaTMet(wrappedChain.calculable) :
    def __init__(self, collection = None, etRatherThanPt = None, metName = None) :
        self.fixes = (collection[0], ("Et" if etRatherThanPt else "Pt") + collection[1])
        self.stash(["Sum","DeltaPseudoJet"])
        self.metName = metName
        self.truncFactor = 0.99
        self.moreName = "met**2 < ht**2 or met**2 = %.2f * ht**2"%self.truncFactor

    def update(self,ignored) :
        ht = self.source[self.Sum]
        met2 = self.source[self.metName].Perp2()
        ht2 = ht*ht
        if met2>ht2 :
            met2= ht2*self.truncFactor
        self.value = 0.5 * ( ht - self.source[self.DeltaPseudoJet] ) / math.sqrt( ht2 - met2 ) if ht2-met2 else 0
##############################
class DiJetAlpha(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Indices","CorrectedP4"])
    def update(self,ignored) :
        indices = self.source[self.Indices]
        if len(indices)!=2 :
            self.value=None
            return
        p4s = self.source[self.CorrectedP4]
        mass = (p4s.at(indices[0]) + p4s.at(indices[1])).M()
        self.value = p4s.at(indices[1]).pt() / mass  if mass > 0.0 else None
##############################
class DeltaX01(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Indices","CorrectedP4"])
        
    def update(self,ignored) :
        self.value={}
        indices = self.source[self.Indices]
        if len(indices)<2 :
            self.value["phi"]=None
            self.value["eta"]=None
            self.value["R"]=None
            return
        p4s = self.source[self.CorrectedP4]
        jet0 = p4s.at(indices[0])
        jet1 = p4s.at(indices[1])
        self.value["phi"] = r.Math.VectorUtil.DeltaPhi(jet0,jet1)
        self.value["R"  ] = r.Math.VectorUtil.DeltaR(jet0,jet1)
        self.value["eta"] = jet0.eta()-jet1.eta()
##############################
class DeltaPhiStar(wrappedChain.calculable) :
    def __init__(self, collection = None, extraName = "") :
        self.fixes = (collection[0],collection[1]+extraName)
        self.stash(["CorrectedP4"],collection)
        self.stash(["Indices","SumP4"])

    def update(self,ignored) :
        self.value = []
        sumP4 = self.source[self.SumP4]
        if not sumP4 : return
        jets = self.source[self.CorrectedP4]
        self.value = sorted([ (abs(r.Math.VectorUtil.DeltaPhi(jets.at(i),jets.at(i)-sumP4)), i) for i in self.source[self.Indices] ])
##############################
class DeltaPhiMht(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4","SumP4"])
    def update(self,ignored) :
        sumP4 = self.source[self.SumP4]
        p4s = self.source[self.CorrectedP4]
        self.value = map(r.Math.VectorUtil.DeltaPhi, [-sumP4]*len(p4s), p4s)
##############################
class MhtSensitivity(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Pt","Mht","DeltaPhiMht"])
    def sensitivity(self,pt,dphi) :
        return math.sqrt(pt) / self.source[self.Mht] * math.cos(dphi)
    def update(self,ignored) :
        self.value = map(self.sensitivity, self.source[self.Pt], self.source[self.DeltaPhiMht])
##############################
class MhtProjection(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Pt","Mht","DeltaPhiMht"])
    def projection(pt,dphi) :
        return self.source[self.Mht] / math.sqrt(pt) * math.cos(dphi)
    def update(self,ignored) :
        self.value = map(self.projection, self.source[self.Pt], self.source[self.DeltaPhiMht] )
##############################
class MaxAbsMhtSensitivity(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Indices","MhtSensitivity"])
    def update(self,ignored) :
        indices = self.source[self.Indices]
        sens = self.source[self.MhtSensitivity]
        self.value = None if not indices else max([(abs(sens[i]),sens[i]) for i in indices])[1]
##############################
class MaxMhtSensitivity(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Indices","MhtSensitivity"])
    def update(self,ignored) :
        indices = self.source[self.Indices]
        sens = self.source[self.MhtSensitivity]
        self.value = None if not indices else max([sens[i] for i in indices])
###############################
class MhtCombinedSensitivity(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Indices","Pt","Mht","DeltaPhiMht"])
    def update(self,ignored) :
        mht = self.source[self.Mht]
        indices = self.source[self.Indices]
        pt = self.source[self.Pt]
        dphi = self.source[self.DeltaPhiMht]
        self.value = None if not indices else \
                     math.sqrt( sum([ pt[i]*(math.cos(dphi[i]))**2 for i in indices]) ) / mht
##############################
class MaxProjMht(wrappedChain.calculable) :
    def __init__(self,collection = None) :
        self.fixes = collection
        self.stash(["Indices","MhtProjection"])
    def update(self,ignored) :
        indices = self.source[self.Indices]
        mhtProj = self.source[self.MhtProjection]
        self.value = None if not indices else max([mhtProj[i] for i in indices])
#####################################
class MhtOverMet(wrappedChain.calculable) :
    @property
    def name(self) : return "%sMht%sOver%s" %(self.fixes[0], self.fixes[1], self.met)

    def __init__(self, jets, met) :
        self.met = met
        self.fixes = jets
        self.stash(["SumP4"])
        
    def update(self, ignored) :
        self.value = self.source[self.SumP4].pt()/self.source[self.met].pt() if self.source[self.SumP4] else None
#####################################
class MhtMinusMetOverMeff(wrappedChain.calculable) :
    @property
    def name(self) : return "%sMhtMinus%sOverMeff%s"%(self.fixes[0], self.met, self.fixes[1])
    
    def __init__(self, jets, etRatherThanPt, met) :
        var = "Et" if etRatherThanPt else "Pt"
        self.fixes = (jets[0], var+jets[1])
        self.met = met
        self.stash(["Mht"], jets)
        self.stash(["Meff"])
        self.moreName = "%s%s; %s; %s"%(self.fixes[0], self.fixes[1], self.met, var)
        
    def update(self, ignored) :
        self.value = (self.source[self.Mht] - self.source[self.met].pt())/self.source[self.Meff]
#####################################
class DeadEcalIndices(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["CorrectedP4"])
        self.moreName = "dR < 0.5"

    def deadEcalIndices(self,p4) :
        deadTP = self.source["ecalDeadTowerTrigPrimP4"]
        indices = []
        for i in range(deadTP.size()) :
            if 0.5 > r.Math.VectorUtil.DeltaR(deadTP.at(i),p4) : indices.apppend(i)
        return indices

    def update(self,ignored) :
        self.value = map( self.deadEcalIndices, self.source[self.CorrectedP4] )
#####################################
class ecalDeadTowerMatchedJetIndices(wrappedChain.calculable) :
    @property
    def name(self) : return "ecalDeadTowerMatched%sIndices%s"%self.cs

    def __init__(self, collection) :
        self.cs = collection
        self.moreName = "tp.Et()>0, dR(tp,%s%s)<0.5"%self.cs

    def matchingJetIndex(self,tpP4) :
        jetP4s = self.source["%sCorrectedP4%s"%self.cs]
        for i in self.source["%sIndices%s"%self.cs] :
            p4= jetP4s[i]
            ptetaphieV4 = r.Math.PtEtaPhiEVector(p4.pt(),p4.eta(),p4.phi(),p4.E())
            if r.Math.VectorUtil.DeltaR(tpP4,ptetaphieV4) < 0.5:
                return i
        return -1

    def update(self,ignored) :
        self.value = map(self.matchingJetIndex,self.source["ecalDeadTowerTrigPrimP4"])
#####################################
class deadEcalDR(wrappedChain.calculable) :
    @property
    def name(self) : return "%sDeadEcalDR%s%s"%(self.jets[0], self.jets[1], self.extraName)
    
    def __init__(self, jets = None, extraName = "", minNXtals = None, checkCracks = True, maxDPhiStar = 0.5) :
        for item in ["jets","extraName","minNXtals","checkCracks","maxDPhiStar"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStar%s%s"%(self.jets[0], self.jets[1], self.extraName)
        self.moreName = "%s%s; nXtal>=%d; cracks %schecked"%(self.jets[0], self.jets[1], self.minNXtals, "" if self.checkCracks else "NOT ")

    def oneJetDRs(self, jet) :
        out = []
        for iRegion in range(self.source["ecalDeadTowerTrigPrimP4"].size()) :
            region = self.source["ecalDeadTowerTrigPrimP4"].at(iRegion)
            nDeadXtals = self.source["ecalDeadTowerNBadXtals"].at(iRegion)
            out.append( (r.Math.VectorUtil.DeltaR(jet, region), nDeadXtals) )
        if self.checkCracks :
            eta = jet.eta()
            out.append( (abs(eta-1.5), self.minNXtals) )
            out.append( (abs(eta+1.5), self.minNXtals) )
        return out

    def DR(self, dRs) :
        nDeadXtals = 0
        for dr,nDead in sorted(dRs) :
            nDeadXtals += nDead
            if nDeadXtals>=self.minNXtals : return dr
        return None
    
    def update(self, ignored) :
        self.value = []
        dps = self.source[self.dps]
        if not dps : return

        for dPhiStar,iJet in dps :
            if dPhiStar > self.maxDPhiStar : break
            dr = self.DR(self.oneJetDRs(self.source["%sCorrectedP4%s"%self.jets].at(iJet)))
            if dr!=None : self.value.append(dr)
        self.value.sort()
##############################
class ResidualCorrectionsFromFile(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.buildLists(self.fileName(collection))

    def fileName(self, collection) :
        fileDict = {}
        fileDict[(     "ak5Jet","Pat")] = "data/Spring10DataV2_L2L3Residual_AK5Calo.txt"
        fileDict[(   "xcak5Jet","Pat")] = "data/Spring10DataV2_L2L3Residual_AK5Calo.txt"
        fileDict[(  "ak5JetJPT","Pat")] = "data/Spring10DataV2_L2L3Residual_AK5JPT.txt"
        fileDict[("xcak5JetJPT","Pat")] = "data/Spring10DataV2_L2L3Residual_AK5JPT.txt"
        fileDict[(   "ak5JetPF","Pat")] = "data/Spring10DataV2_L2L3Residual_AK5PF.txt"
        fileDict[( "xcak5JetPF","Pat")] = "data/Spring10DataV2_L2L3Residual_AK5PF.txt"

        fileDict[("ak5JetPFGenJet","Pat")] = None
        fileDict[("ak5JetPF2PAT","Pat")] = None
        fileDict[("xcak5JetPF2PAT","Pat")] = None
        assert collection in fileDict,"residual corrections file for %s%s not found"%collection
        return fileDict[collection]
    
    def buildLists(self, fileName) :
        self.etaLo  = []
        self.etaHi  = []
        self.p      = []

        if not fileName : return
        inFile = open(fileName)
        for line in inFile :
            if "{" in line : continue
            fields = line.split()
            self.etaLo.append( float(fields[0]) )
            self.etaHi.append( float(fields[1]) )
            self.p.append( (float(fields[5]), float(fields[6]), float(fields[7])) )
        inFile.close()

    def update(self, ignored) :
        self.value = {"etaLo":self.etaLo, "etaHi":self.etaHi, "p":self.p}
#####################################
class Resolution(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4"])
        self.resFuncs = sorted( utils.cmsswFuncData(self.fileName(collection), par="sigma")) if self.fileName(collection) else []

    @staticmethod
    def fileName(collection) :
        names = {}
        for pre in ["ak5Jet","xcak5Jet"] : names[(pre,"Pat")] = "data/Spring10_PtResolution_AK5Calo.txt"
        for pre in ["ak5JetPF","xcak5JetPF"] : names[(pre,"Pat")] = "data/Spring10_PtResolution_AK5PF.txt"
        if collection not in names : return None
        return names[collection]
        
    def res(self, p4) :
        if not self.resFuncs: return None
        etaBin = max(0,bisect.bisect(self.resFuncs,(p4.eta(),None,None))-1)
        return self.resFuncs[etaBin][2].Eval(p4.pt())
    
    def update(self, ignored) :
        self.value = utils.hackMap(self.res, self.source[self.CorrectedP4])
#####################################
class CovariantResolution2(wrappedChain.calculable) :
    '''[[xx,xy],[xy,yy]] in the transverse plane.'''

    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["CorrectedP4","Resolution"])

    @staticmethod
    def matrix(p4,res) :
        phi = p4.phi()
        return p4.Perp2() * res**2 * np.outer(*(2*[[math.cos(phi),math.sin(phi)]]))

    def update(self,ignored) : 
        self.value = utils.hackMap(self.matrix , self.source[self.CorrectedP4] , self.source[self.Resolution] )
#####################################
class ProbabilityGivenBQN(calculables.secondary) :
    def __init__(self, collection = None, bvar = None, binning = (0,0,0), samples = ('',[]), tag = None,) :
        self.fixes = collection
        self.__name = ('%s'+bvar+self.__class__.__name__+'%s')%self.fixes
        self.bvar = ("%s"+bvar+"%s")%xcStrip(collection)
        for item in ['binning','samples','tag'] : setattr(self,item,eval(item))
        self.stash(['Indices','IndicesGenB','IndicesGenWqq'])
        self.moreName = (tag if tag!=None else '') + '; ' + ','.join(samples[1] if samples[1] else [samples[0]])
    @property
    def name(self) : return self.__name

    def onlySamples(self) : return [self.samples[0]]

    def setup(self,*_) :
        hists = self.fromCache([self.samples[0]],['B','Q','N'], tag = self.tag)
        self.histsBQN = [hists[self.samples[0]][jetType] for jetType in ['B','Q','N']]
        for hist in filter(None,self.histsBQN) : hist.Scale(1./hist.Integral(0,hist.GetNbinsX()+1),"width")
        
    def uponAcceptance(self,ev) :
        if ev['isRealData'] : return
        indices = ev[self.Indices]
        iB = ev[self.IndicesGenB]
        iQ = ev[self.IndicesGenWqq]
        bvar = ev[self.bvar]
        for i in indices :
            jetType = "B" if i in iB else "Q" if i in iQ else "N"
            self.book.fill(bvar.at(i), jetType, *self.binning, title = ";%s (%s);events / bin"%(self.bvar,jetType))
    
    def update(self,_) :
        self.value = [tuple(hist.GetBinContent(hist.FindFixBin(bvar)) if hist else 0 for hist in self.histsBQN)
                      for bvar in self.source[self.bvar]]
        
    def organize(self,org) :
        if org.tag != self.tag : return
        if self.samples[1] :
            missing = [s for s in self.samples[1] if s not in [ss['name'] for ss in org.samples]]
            if missing: print self.name, "-- no such samples :\n", missing
            org.mergeSamples( targetSpec = {'name':self.samples[0]}, sources = self.samples[1] )
        else: org.mergeSamples( targetSpec = {'name':self.samples[0]}, allWithPrefix = self.samples[0] )
#####################################
class CorrectedP4(wrappedChain.calculable) :
    def __init__(self, genJets = None) : #purposefully not called collection
        self.fixes = genJets
        self.stash(["P4"])
    def update(self, ignored) :
        self.value = self.source[self.P4]
#####################################
class P4(wrappedChain.calculable) :
    def __init__(self, genJets = None) : #purposefully not called collection
        self.fixes = genJets
        self.stash(["P4"], ("gen%sJets"%(self.fixes[0].replace("Jet","").replace("PF","").replace("JPT","")), "") )
    def update(self, ignored) :
        self.value = self.source[self.P4]
#####################################
class nJetsWeight(wrappedChain.calculable) :
    def __init__(self, jets, nJets = []) :
        self.fixes = jets
        self.stash(["Indices"])
        self.nJets = nJets
    def update(self, ignored) :
        self.value = 1.0 if len(self.source[self.Indices]) in self.nJets else None
#####################################
class IndicesMinDeltaR(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Indices","CorrectedP4"])
    def update(self,ignored) :
        p4 = self.source[self.CorrectedP4]
        indices = self.source[self.Indices]
        self.value = min(itertools.combinations(indices,2), key = lambda i: r.Math.VectorUtil.DeltaR(p4[i[0]],p4[i[1]])) if len(indices)>1 else (None,None)
#####################################
class Kt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["IndicesMinDeltaR","CorrectedP4"])
        self.moreName = "min(pt_i,pt_j) * dR(i,j); ij with minDR; %s%s"%collection
    def update(self,ignored) :
        p4 = self.source[self.CorrectedP4]
        i,j = self.source[self.IndicesMinDeltaR]
        self.value = min(p4[i].pt(),p4[j].pt()) * r.Math.VectorUtil.DeltaR(p4[i],p4[j]) if j else -1
######################################
class ComboPQBRawMassWTop(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['Indices','CorrectedP4'])
    def update(self,_) :
        p4 = self.source[self.CorrectedP4]
        self.value = {}
        for iPQB in itertools.permutations(self.source[self.Indices],3) :
            if iPQB[0]>iPQB[1] : continue
            _,W,t = np.cumsum([p4[i] for i in iPQB])
            self.value[iPQB] = (W.M(),t.M())
######################################
class ComboPQBDeltaRawMassWTop(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['ComboPQBRawMassWTop'])
    def update(self,_) : self.value = dict([(key,(val[0]-80.4,val[1]-172)) for key,val in self.source[self.ComboPQBRawMassWTop].iteritems()])
######################################

######################################
class __value__(wrappedChain.calculable) :
    def __init__(self, jets = None, index = 0, Btagged = True ) :
        self.fixes = ("%s%s%d"%(jets[0],'B' if Btagged else '', index), jets[1])
        self.stash(["CorrectedP4","Indices","IndicesBtagged"],jets)
        self.index = index
        self.Btagged = Btagged
    def update(self,_) :
        p4 = self.source[self.CorrectedP4]
        indices = self.source[self.IndicesBtagged if self.Btagged else self.Indices]
        self.value = self.function(p4[indices[self.index]]) if len(indices)>self.index else 0
######################################
class pt(__value__) :
    def function(self, x) : return x.pt()
######################################
class absEta(__value__) :
    def function(self,x) : return abs(x.eta())
######################################
class eta(__value__) :
    def function(self,x) : return x.eta()
######################################

######################################
class DeltaPhiB01(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['CorrectedP4','IndicesBtagged'])
    def update(self,_) :
        p4 = self.source[self.CorrectedP4]
        b = self.source[self.IndicesBtagged]
        self.value = abs(r.Math.VectorUtil.DeltaPhi(p4[b[0]],p4[b[1]]))
######################################
class FourJetPtThreshold(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['Pt', 'Indices'])
    def update(self,_):
        pt = self.source[self.Pt]
        indices = self.source[self.Indices]
        idPt = [pt[i] for i in indices]
        self.value = 0 if len(idPt)<4 else idPt[3]
######################################
class FourJetAbsEtaThreshold(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(['CorrectedP4', 'Indices'])
    def update(self,_):
        p4 = self.source[self.CorrectedP4]
        indices = self.source[self.Indices]
        idAbsEta = sorted([abs(p4.at(i).eta()) for i in indices])
        self.value = 0 if len(idAbsEta)<4 else idAbsEta[3]
######################################
class PileUpPtFraction(wrappedChain.calculable) :
    def __init__(self, collection = None ) :
        self.fixes = collection
        self.stash(['SumP3withPrimaryHighPurityTracks',
                    'SumP3withPileUpHighPurityTracks'], xcStrip(collection))
    def update(self,_) :
        pri = self.source[self.SumP3withPrimaryHighPurityTracks]
        pu = self.source[self.SumP3withPileUpHighPurityTracks]
        self.value = [pu[i].rho()/max(0.001,pu[i].rho()+pri[i].rho()) for i in range(len(pri))]
