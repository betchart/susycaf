from wrappedChain import *
import math,collections
import calculables,utils

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
class IndicesOther(calculables.indicesOther) :
    def __init__(self, collection = None) :
        super(IndicesOther, self).__init__(collection)
        self.moreName = "pass ptMin; fail jetID or etaMax"
##############################
class Indices(wrappedChain.calculable) :
    def __init__(self, collection = None, ptMin = None, etaMax = None, flagName = None, extraName = ""):
        self.fixes = (collection[0],collection[1]+extraName)
        self.stash(["IndicesOther","IndicesKilled"])
        self.stash(["CorrectedP4"],collection)
        self.extraName = extraName
        self.pt2Min = ptMin*ptMin
        self.etaMax = etaMax
        self.flag = None if not flagName else \
                    ( "%s"+flagName+"%s" if xcStrip(collection)[0][-2:] != "PF" else \
                      "%sPF"+flagName+"%s" ) % xcStrip(collection)
        self.moreName = "pT>=%.1f GeV; |eta|<%.1f; %s"% (ptMin, etaMax, flagName if flagName else "")

    def update(self,ignored) :
        self.value = []
        p4s    = self.source[self.CorrectedP4]
        other  = self.source[self.IndicesOther]  if not self.extraName else []
        killed = self.source[self.IndicesKilled] if not self.extraName else []
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
####################################
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
        self.value = [p4.pt() for p4 in self.source[self.CorrectedP4]]
##############################
class SumPt(wrappedChain.calculable) :
    def __init__(self, collection = None) :
        self.fixes = collection
        self.stash(["Pt","Indices"])
    def update(self,ignored) :
        pts = self.source[self.Pt]
        self.value = reduce( lambda x,i: x+pts[i], self.source[self.Indices] , 0)
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
        self.value = reduce( lambda x,i: x+p4s.at(i), indices, r.LorentzV()) if len(indices) else None
####################################
class SumP4Ignored(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["CorrectedP4","IndicesIgnored"])
    def update(self,ignored) :
        p4s = self.source[self.CorrectedP4]
        self.value = reduce( lambda x,i: x+p4s.at(i), self.source[self.IndicesIgnored], r.LorentzV())
####################################
class Mht(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["SumP4"])
    def update(self,ignored) :
        self.value = self.source[self.SumP4].pt()
####################################
class MhtIgnored(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["SumP4Ignored"])
    def update(self,ignored) :
        self.value = self.source[self.SumP4Ignored].pt()
####################################
class Meff(wrappedChain.calculable) :
    def __init__(self,collection) :
        self.fixes = collection
        self.stash(["Mht","SumPt"])
    def update(self,ignored) :
        self.value = self.source[self.Mht]+self.source[self.SumPt]
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
        self.value = reduce(lambda x,p4: max(x+p4,x-p4,key=lambda p:p.pt()), [p4s.at(i) for i in self.source[self.Indices]], r.LorentzV())
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
class CosDeltaPhiStar(wrappedChain.calculable) :
    def __init__(self,collection=None) :
        self.fixes = collection
        self.stash(["DeltaPhiStar"])
    def update(self,ignored) :
        self.value = math.cos(self.source[self.DeltaPhiStar])
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
        self.stash(["Meff","PartialSumP4Area"])
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
        
        diff = [0.] * (1<<len(indices))
        for j in indices :
            pt = p4s.at(j).pt() if not self.etRatherThanPt else p4s.at(j).Et()
            for i in range( len(diff) ) :
                diff[i] += pt * (1|-(1&(i>>j)))
        
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
        self.value = self.source[self.Mht]/self.source[self.SumEt]
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
class AlphaTWithPhoton1PtRatherThanMht(wrappedChain.calculable) :
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
        self.value = {}
        self.value["DeltaPhiStar"] = None
        self.value["DeltaPhiStarJetIndex"] = None

        sumP4 = self.source[self.SumP4]
        if not sumP4 : return
        jets = self.source[self.CorrectedP4]

        dPhi = [ (abs(r.Math.VectorUtil.DeltaPhi(jets.at(i),jets.at(i)-sumP4)),i) for i in self.source[self.Indices] ]
        self.value["DeltaPhiStar"],self.value["DeltaPhiStarJetIndex"] = min(dPhi)
##############################
class DeltaPhiStarIncludingPhotons(wrappedChain.calculable) :
    def __init__(self, collection = None, photons = None, extraName = "") :
        self.fixes = (collection[0],collection[1]+extraName)
        self.stash(["CorrectedP4"],collection)
        self.stash(["Indices","SumP4PlusPhotons"])
        self.photonP4 = '%sP4%s' % photons
        self.photonIndices = '%sIndices%s' % photons
        
    def update(self,ignored) :
        self.value = {}
        self.value["DeltaPhiStar"] = None
        self.value["DeltaPhiStarJetIndex"] = None
        self.value["DeltaPhiStarPhotonIndex"] = None

        sumP4 = self.source[self.SumP4PlusPhotons]
        if not sumP4 : return        
        jets = self.source[self.CorrectedP4]
        photons = self.source[self.photonP4]

        dPhi = [ (abs(r.Math.VectorUtil.DeltaPhi(    jets.at(i),    jets.at(i)-sumP4)),    i, None) for i in self.source[self.Indices]] +\
               [ (abs(r.Math.VectorUtil.DeltaPhi( photons.at(i), photons.at(i)-sumP4)), None,    i) for i in self.source[self.photonIndices]]

        self.value["DeltaPhiStar"],self.value["DeltaPhiStarJetIndex"],self.value["DeltaPhiStarPhotonIndex"] = min(dPhi)
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
class mhtIncludingPhotonsOverMet(wrappedChain.calculable) :

    def __init__(self, jets, met, etRatherThanPt) :
        self.jets = jets
        self.met = met
        self.etRatherThanPt = etRatherThanPt
        self.moreName = "%s%s; %s; %s"%(self.jets[0], self.jets[1], self.met, "ET" if self.etRatherThanPt else "pT")
        self.mht = "%sSumP4PlusPhotons%s"%self.jets
        
    def update(self, ignored) :
        self.value = self.source[self.mht].pt()/self.source[self.met].pt()
#####################################
class mhtOverMet(wrappedChain.calculable) :
    def name(self) : return "%sMht%s_Over_%s" %(self.jets[0],self.jets[1],self.met)

    def __init__(self, jets, met) :
        self.jets = jets
        self.met = met
        self.mht = "%sSumP4%s"%self.jets
        
    def update(self, ignored) :
        self.value = self.source[self.mht].pt()/self.source[self.met].pt() if self.source[self.mht] else None
#####################################
class metPlusPhoton(wrappedChain.calculable) :
            
    def __init__(self, met, photons, photonIndex) :
        self.met = met
        self.photons = photons
        self.photonIndex = photonIndex
        self.moreName = "%s + %s%s[index[%d]]"%(self.met, self.photons[0], self.photons[1], self.photonIndex)
        
    def update(self, ignored) :
        index = self.source["%sIndices%s"%self.photons][self.photonIndex]
        self.value = self.source[self.met] + self.source["%sP4%s"%self.photons].at(index)
#####################################
class mhtMinusMetOverMeff(wrappedChain.calculable) :

    def __init__(self, jets, met, etRatherThanPt) :
        self.jets = jets
        self.met = met
        self.etRatherThanPt = etRatherThanPt
        self.moreName = "%s%s; %s; %s"%(self.jets[0], self.jets[1], self.met, "ET" if self.etRatherThanPt else "pT")
        self.mht = "%sSumP4%s"%self.jets
        self.ht  = "%sSumEt%s"%self.jets if self.etRatherThanPt else "%sSumPt%s"%self.jets
        
    def update(self, ignored) :
        mht = self.source[self.mht].pt()
        self.value = (mht - self.source[self.met].pt())/(self.source[self.ht] + mht)
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
    def name(self) : return "%sDeadEcalDR%s%s"%(self.jets[0], self.jets[1], self.extraName)
    
    def __init__(self, jets = None, extraName = "", minNXtals = None) :
        for item in ["jets","extraName","minNXtals"] :
            setattr(self,item,eval(item))
        self.dps = "%sDeltaPhiStar%s%s"%(self.jets[0], self.jets[1], self.extraName)
        self.badJet = r.Math.LorentzVector(r.Math.PtEtaPhiE4D('double'))(0.0,0.0,0.0,0.0)
        self.moreName = "%s%s; nXtal>=%d"%(self.jets[0], self.jets[1], self.minNXtals)
        
    def update(self, ignored) :
        jet = self.source["%sCorrectedP4%s"%self.jets].at(self.source[self.dps]["DeltaPhiStarJetIndex"])
        self.badJet.SetCoordinates(jet.pt(),jet.eta(),jet.phi(),jet.E())

        dRs = []
        for iRegion,region in enumerate(self.source["ecalDeadTowerTrigPrimP4"]) :
            if self.source["ecalDeadTowerNBadXtals"].at(iRegion)<self.minNXtals : continue
            dRs.append(r.Math.VectorUtil.DeltaR(self.badJet,region))
        self.value = min(dRs) if len(dRs) else None
##############################
class ResidualCorrectionsFromFile(wrappedChain.calculable) :
    def __init__(self, jets = None) :
        self.fixes = jets

        fileDict = {}
        fileDict[(    "ak5Jet","Pat")] = "Spring10DataV2_L2L3Residual_AK5Calo.txt"
        fileDict[(  "xcak5Jet","Pat")] = "Spring10DataV2_L2L3Residual_AK5Calo.txt"
        fileDict[(  "ak5JetPF","Pat")] = "Spring10DataV2_L2L3Residual_AK5PF.txt"
        fileDict[("xcak5JetPF","Pat")] = "Spring10DataV2_L2L3Residual_AK5PF.txt"
        assert jets in fileDict,"residual corrections file for %s%s not found"%jets

        self.etaLo  = []
        self.etaHi  = []
        self.p      = []
        inFile = open(fileDict[jets])
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
