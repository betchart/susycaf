from supy import calculables,utils,wrappedChain
import collections,os, ROOT as r
try:
    import numpy as np
except:
    pass

#####################################
class lowestUnPrescaledTrigger(wrappedChain.calculable) :
    def __init__(self, sortedListOfPaths = []) :
        self.sortedListOfPaths = sortedListOfPaths
        self.cached = dict()
        self.moreName = "lowest unprescaled of " + utils.contract(self.sortedListOfPaths)

    def update(self, ignored) :
        key = (self.source["run"],self.source["lumiSection"])
        if key not in self.cached :
            self.cached[key] = None
            for path in self.sortedListOfPaths :
                if self.source["prescaled"][path]==1 :
                    self.cached[key] = path
                    break
        self.value = self.cached[key]
##############################
class TriggerWeight(calculables.secondary) :
    '''Probability that the event was triggered.'''
    
    def __init__(self, samples, tag = None, collection = ('muon','PF'), var = 'Pt', index = 'TriggeringIndex', triggers = [], thresholds = [], unreliable = {}) :
        self.fixes = collection
        self.var = "%s%s%s"%(self.fixes[0],var,self.fixes[1])
        self.index = "%s%s%s"%(self.fixes[0],index,self.fixes[1])
        self.binning = (200,0,200)
        for item in ['triggers','thresholds','tag','samples','unreliable'] : setattr(self,item,eval(item))

    def onlySamples(self) : return self.samples

    def setupDicts(self) :
        dd = collections.defaultdict
        self.epochLumis = dd(lambda : dd(set)) #set of lumis by run by (prescale set)
        self.lumis = dd(set) #set of lumis by run

    def setup(self,*_) :
        self.setupDicts()
        hists = self.fromCache( self.samples, ["susyTreeLumi",self.name], self.tag)
        if not all(all(hs.values()) for hs in hists.values()) :
            self.weights = r.TH1D('empty','',1,0,1)
            for i in range(3) : self.weights.SetBinContent(i, 1)
            return
        lumis = [ hists[sample]['susyTreeLumi'].GetBinContent(1) for sample in self.samples ]
        weights = [ hists[sample][self.name] for sample in self.samples ]
        for lumi,weight in zip(lumis,weights) : weight.Scale(lumi)
        self.weights = weights[0].Clone("random")
        for w in weights[1:] : self.weights.Add(w)
        self.weights.Scale(1./sum(lumis))
        for i in range(self.weights.GetNbinsX()+2) : assert 0 <= self.weights.GetBinContent(i) <= 1

    def triggerFired(self, val, triggered) :
        for thresh,trig in zip(self.thresholds,self.triggers) :
            if thresh > val : return False
            if triggered[trig] and (trig not in self.unreliable or
                                    self.source['prescaled'][trig] not in self.unreliable[trig]):
                return True
        return False

    def update(self,_) :
        index = self.source[self.index]
        self.value = (None if index is None else
                      self.weights.GetBinContent(self.weights.FindFixBin(self.source[self.var][index])) if not self.source['isRealData'] else
                      1 if self.triggerFired(self.source[self.var][index], self.source['triggered']) else None )

    def uponAcceptance(self,ev) :
        index = ev[self.index]
        val = ev[self.var][index]
        
        self.book.fill(ev[self.name], 'value_%s'%self.name, 100, 0, 1, title = ';%s;events / bin'%self.name)
        self.book.fill(val, self.var,              *self.binning, title = ';%s;events / bin'%self.var)
        self.book.fill(val, self.var+'unweighted', *self.binning, title = ';%s;events / bin'%self.var, w = 1)

        if not ev['isRealData'] : return
        
        run,lumi = (ev["run"],ev["lumiSection"])
        if lumi in self.lumis[run] : return
        key = tuple([ev["prescaled"][trig] for trig in self.triggers])
        if self.unreliable : key = tuple([0 if trig in self.unreliable and ps in self.unreliable[trig] else ps for ps,trig in zip(key,self.triggers)])

        self.epochLumis[key][run].add(lumi)
        self.lumis[run].add(lumi)

    @property
    def staticEpochLumis(self) : return dict((epoch,dict(self.epochLumis[epoch].iteritems())) for epoch in self.epochLumis)

    def varsToPickle(self) : return ["staticEpochLumis"]
    def outputSuffix(self) : return "_%s/"%self.name

    def mergeFunc(self,products) :
        self.setupDicts()
        for eLumis in products["staticEpochLumis"] :
            for epoch in eLumis :
                for run in eLumis[epoch] :
                    self.epochLumis[epoch][run] |= eLumis[epoch][run]
        if not self.epochLumis : return

        lumiDir = self.outputFileName
        if not os.path.exists(lumiDir) : utils.mkdir(lumiDir)
        
        lumis = utils.luminosity.recordedInvMicrobarnsShotgun( [utils.jsonFromRunDict(self.epochLumis[epoch]) for epoch in self.epochLumis ] , cores = 4, cacheDir = lumiDir)
        probs = [ [1./prescale if prescale else 0 for prescale in epoch] for epoch in self.epochLumis ]
        inclu = [ [utils.unionProbability(prob[:i+1]) for i in range(len(prob))] for prob in probs ]
        thresholds = sorted(set(self.thresholds))
        inclusives = [ [max([0]+[p for p,t in zip(inc,self.thresholds) if t is thresh]) for thresh in thresholds] for inc in inclu ]
        weights = np.array(lumis).dot(inclusives) / sum(lumis)

        # write total lumi and weight by threshold
        lumiHist = r.TH1D('susyTreeLumi','luminosity from susyTree;;1/pb',1,0,1)
        lumiHist.SetBinContent(1,sum(lumis))
        lumiHist.Write()

        weightHist = r.TH1D(self.name,";%s;%s"%(self.var,self.name), len(thresholds), np.array([0.]+thresholds+[max(thresholds)+10]))
        for i,w in enumerate(weights) : weightHist.SetBinContent(i+2, w)
        weightHist.SetBinContent(len(thresholds)+3, 1)
        weightHist.Write()
        
