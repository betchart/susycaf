from supy import wrappedChain,utils
import bisect,math, ROOT as r
##############################
class xcJet_SingleLepton(wrappedChain.calculable) :

    @property
    def name(self) : return self.name_

    def __init__(self, xcjets = None, leptons = None, indices = None ) :
        self.name_ = "CorrectedP4".join(xcjets)
        self.p4jet = self.name_[2:]
        self.p4lep = "P4".join(leptons)
        self.indices = indices.join(leptons)
        self.moreName = self.p4jet +" without " + self.p4lep + self.indices.join(['[','[0]]'])

    def update(self,_) :
        jets = self.source[self.p4jet]
        lep =  self.source[self.p4lep][next(iter(self.source[self.indices]), None )]
        self.value = utils.vector()
        for iJet in range(len(jets)) :
            jet = jets[iJet]
            self.value.push_back( jet - lep
                                  if lep and 0.5>r.Math.VectorUtil.DeltaR(jet,lep) else
                                  jet )
##############################
class xcJet(wrappedChain.calculable) :
    @property
    def name(self) : return "%sCorrectedP4%s"%self.xcjets

    def __init__(self,xcjets = None, applyResidualCorrectionsToData = None,
                 gamma    = None, gammaDR    = 0,
                 electron = None, electronDR = 0,
                 muon     = None, muonDR     = 0,
                 correctForMuons = None,
                 jesAbs = 1,
                 jesRel = 0 ) :
        self.value = utils.vector()
        self.jetP4Source = "CorrectedP4".join(xcjets)[2:]
        if applyResidualCorrectionsToData : print "WARNING: you are applying Spring10 Residual corrections to data!"

        for item in ["xcjets", "applyResidualCorrectionsToData", "correctForMuons", "jesAbs", "jesRel"] :
            setattr(self, item, eval(item))

        self.other = dict( [ (i,(eval(i),eval(i+"DR"))) for i in ["gamma","electron","muon"]] )
        self.resCorr = ("%sResidualCorrectionsFromFile%s"%self.xcjets)
        self.moreName = "; ".join(["%s%sDR<%.2f"%(v[0]+(v[1],)) for v in filter(lambda v: v[0], self.other.values())])
        if jesAbs!=1.0 or jesRel!=0.0:
            self.moreName2 += "jes corr: %.2f*(1+%.2f|eta|)"%(jesAbs,jesRel)

    def resPtFactor(self, index, pt) :
        p = self.source[self.resCorr]["p"][index]
        return p[0]-abs(p[1])*math.atan( math.log10( min(1.0, pt/p[2]) ) )
    
    def resFactor(self, p4) :
        if self.applyResidualCorrectionsToData and self.source['isRealData'] :
            etaLo = self.source[self.resCorr]["etaLo"]
            etaHi = self.source[self.resCorr]["etaHi"]
            index = max(0, bisect.bisect(etaLo, p4.eta())-1)
            if index==0 or index==len(etaLo)-1 :
                return self.resPtFactor(index, p4.pt())
            else :
                args = (p4.eta(),
                        [(etaLo[i]+etaHi[i])/2.0      for i in range(index-1, index+2)],
                        [self.resPtFactor(i, p4.pt()) for i in range(index-1, index+2)],
                        )
            return utils.quadraticInterpolation(*args)
        else :
            return 1.0
        
    def jes(self, p4) : return p4 * self.jesAbs*(1+self.jesRel*abs(p4.eta())) * self.resFactor(p4)

    def update(self,ignored) :
        jetP4s = self.source[self.jetP4Source]
        killed = self.source["%sIndicesKilled%s"%self.xcjets]
        nMuonsMatched = self.source["%sNMuonsMatched%s"%self.xcjets]
        matchedMuons = []

        self.value = utils.vector()
        for iJet in range(len(jetP4s)) :
            self.value.push_back(self.jes(jetP4s[iJet]))
            
            if self.matchesIn("gamma",self.value[iJet]) \
            or self.matchesIn("electron",self.value[iJet]) :
                killed.add(iJet)
                continue

            for p4 in self.matchesIn("muon",self.value[iJet], exitEarly=False, indicesStr="%sIndicesNonIso%s") :
                matchedMuons.append(p4)
                nMuonsMatched[iJet] += 1
                if self.correctForMuons: self.value[iJet] += p4

        if self.other["muon"][0] :
            nonisomu = self.source["%sIndicesNonIso%s"%self.other["muon"][0]]
            self.source["crock"]["%s%sNonIsoMuonsUniquelyMatched"%self.xcjets]= (len(set(matchedMuons)) == len(nonisomu) == len(matchedMuons))

    def matchesIn(self,label,p4, exitEarly = True, indicesStr = "%sIndices%s") :
        collection,dR = self.other[label]
        if not collection : return False
        indices = self.source[indicesStr % collection]
        objects = self.source["%sP4%s"%collection]
        matches = []
        for i in indices :
            objP4 = objects.at(i)
            if dR > r.Math.VectorUtil.DeltaR(objP4,p4) :
                if exitEarly: return True
                else: matches.append(objP4)
        return matches
##############################
class IndicesUnmatched(wrappedChain.calculable) :
    def __init__(self, collection = None, xcjets=None, DR = 0) :
        self.fixes = collection
        self.stash(["P4","IndicesOther"])
        self.compareJets = ("%sCorrectedP4%s"%xcjets)[2:]
        self.moreName = "%sIndicesOther%s; no dR<%.1f match in %s"%(collection+(DR,self.compareJets))
        for item in ["collection","DR"]: setattr(self,item,eval(item))

    def noJetMatch(self, i) :
        p4 = self.source[self.P4].at(i)
        jets = self.source[self.compareJets]
        for i in range(jets.size()) :
            if self.DR > r.Math.VectorUtil.DeltaR(p4, jets.at(i)) :
                return False
        return True
        
    def update(self,ignored) :
        self.value = filter(self.noJetMatch, self.source[self.IndicesOther])
##############################
class SumP4(wrappedChain.calculable) :
    def __init__(self, jet = None, photon = None, electron = None, muon = None ) :
        self.fixes = ("xc","")
        stuff = ["jet","photon","electron","muon"]
        self.indicesP4s = [("%sIndices%s"%eval(s),
                           "%sP4%s"%eval(s) if s!="jet" else "%sCorrectedP4%s"%eval(s)) for s in stuff]
        self.moreName = ';'.join(["%s: %s%s"%((s,)+eval(s)) for s in stuff])
        self.value = utils.LorentzV()

    def update(self,ignored) :
        self.value.SetPxPyPzE(0,0,0,0)
        self.value = sum(sum([[self.source[p4s][index] for index in self.source[indices]] for indices,p4s in self.indicesP4s],[]),self.value)
##############################
class SumPt(wrappedChain.calculable) :
    def __init__(self, jet = None, photon = None, electron = None, muon = None ) :
        self.fixes = ("xc","")
        stuff = ["jet","photon","electron","muon"]
        self.indicesP4s = [("%sIndices%s"%eval(s),
                           "%sP4%s"%eval(s) if s!="jet" else "%sCorrectedP4%s"%eval(s)) for s in stuff]
        self.moreName = ';'.join(["%s: %s%s"%((s,)+eval(s)) for s in stuff])

    def update(self,ignored) :
        self.value = sum(sum([[self.source[p4s][index].pt() for index in self.source[indices]] for indices,p4s in self.indicesP4s],[]))
