import supy, steps,calculables,samples,os, ROOT as r

def triggerTuple(l = [], keys = []) :
    out = []
    for item in l :
        stem = "HLT"
        for key in keys :
            stem += "_%s%s"%(key, str(item[key]).replace(".","p"))
        for version in item["v"] :
            out.append("%s_v%d"%(stem, version))
    return tuple(out)

#required to be sorted
triggers_ht_2010 = ("HLT_HT100U","HLT_HT100U_v3","HLT_HT120U","HLT_HT140U","HLT_HT150U_v3")

triggers_ht_eps = tuple(["HLT_HT250_MHT60_v%d"%i for i in [2,3,4,6,7]   ]+
                        ["HLT_HT250_MHT70_v%d"%i for i in [1,3,4]       ]+
                        ["HLT_HT250_MHT80_v%d"%i for i in [3,4]         ]+
                        ["HLT_HT250_MHT90_v%d"%i for i in [1]           ]+
                        ["HLT_HT250_MHT100_v%d"%i for i in [1]          ]+
                        ["HLT_HT260_MHT60_v%d"%i for i in [2]           ])

triggers_mht_2011 = triggerTuple(l = [{"HT":250, "MHT":  60, "v":[1,2,3,4,5,6,7]},
                                      {"HT":260, "MHT":  60, "v":[1,2]},
                                      {"HT":250, "MHT":  70, "v":[1,2,3,4]},
                                      {"HT":250, "MHT":  80, "v":[1,2,3,4]},
                                      {"HT":250, "MHT":  90, "v":[1,2,3,4]},
                                      {"HT":250, "MHT": 100, "v":[1,2]},
                                      
                                      {"HT":300, "MHT":  75, "v":[1,2,3,4,5,6,7,8]},
                                      {"HT":300, "MHT":  80, "v":[1,2]},
                                      {"HT":300, "MHT":  90, "v":[1,2]},
                                      
                                      {"HT":350, "MHT":  70, "v":[1,2]},
                                      {"HT":350, "MHT":  80, "v":[1,2]},
                                      {"HT":350, "MHT":  90, "v":[1]},

                                      {"HT":400, "MHT":  80, "v":[1]},
                                      ], keys = ("HT", "MHT"))
                                      
triggers_alphaT_2011 = triggerTuple(l  = [#{"HT":250, "AlphaT": 0.53, "v":range(1,7)},
                                          #{"HT":250, "AlphaT": 0.54, "v":range(2,5)},
                                          #{"HT":250, "AlphaT": 0.55, "v":range(1,3)},
                                          #{"HT":250, "AlphaT": 0.62, "v":range(1,3)},
                                          
                                          {"HT":300, "AlphaT": 0.52, "v":range(1,6)},
                                          {"HT":300, "AlphaT": 0.53, "v":range(1,7)},
                                          #{"HT":300, "AlphaT": 0.54, "v":range(1,3)},
                                          
                                          {"HT":350, "AlphaT": 0.51, "v":range(1,6)},
                                          {"HT":350, "AlphaT": 0.52, "v":range(1,3)},
                                          {"HT":350, "AlphaT": 0.53, "v":range(1,8)},
                                          
                                          {"HT":400, "AlphaT": 0.51, "v":range(1,8)},
                                          {"HT":400, "AlphaT": 0.52, "v":range(1,3)},
                                          
                                          {"HT":450, "AlphaT": 0.51, "v":range(1,3)},
                                          {"HT":450, "AlphaT": 0.52, "v":range(1,3)},
                                          ], keys = ("HT", "AlphaT"))

class hadronicLook(supy.analysis) :
    def parameters(self) :
        objects = self.vary()
        fields =                                                  [ "jet",                        "jetId",     "muonsInJets",           "met",
                                                                    "compJet",                "compJetId", "compMuonsInJets",        "compMet",
                                                                    "muon",                    "electron",          "photon",         "rechit"]

        objects["caloAK5JetMet_recoLepPhot"]   = dict(zip(fields, [("xcak5Jet","Pat"),       "JetIDloose",             False, "metP4AK5TypeII",
                                                                   ("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
                                                                   ("muon","Pat"),     ("electron","Pat"),  ("photon","Pat"),           "Calo",
                                                                   ]))
        
        #objects["pfAK5JetMet_recoLepPhot"]     = dict(zip(fields, [("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
        #                                                           ("xcak5Jet","Pat"),       "JetIDloose",             False, "metP4AK5TypeII",
        #                                                           ("muon","Pat"),     ("electron","Pat"),  ("photon","Pat"),             "PF",
        #                                                           ]))
        
        #objects["pf2patAK5JetMetLep_recoPhot"] = dict(zip(fields, [("xcak5JetPF2PAT","Pat"), "PFJetIDtight",            True,        "metP4PF",
        #                                                           ("xcak5JetPF","Pat"),     "JetIDtight",              True,        "metP4PF",
        #                                                           ("muon","PF"),       ("electron","PF"),  ("photon","Pat"),             "PF",
        #                                                           ]))
        
        return { "objects": objects,
                 "nJetsMinMax" :      self.vary(dict([ ("ge2",(2,None)),  ("2",(2,2)),  ("ge3",(3,None)),  ("3",(3,3)) ]       [0:1] )),
                 "mcSoup" :           self.vary(dict([ ("pythia6","py6"), ("pythia8","py8"), ("madgraph","mg") ] [0:1] )),
                 "etRatherThanPt" : [True,False][0],
                 "lowPtThreshold" : 30.0,
                 "lowPtName" : "lowPt",
                 "highPtThreshold" : 50.0,
                 "highPtName" : "highPt",
                 "tanBeta" : [None, 3, 10, 50][0],
                 "thresholds": self.vary(dict( [("275",        (275.0, 325.0, 100.0, 50.0)),#0
                                                ("325",        (325.0, 375.0, 100.0, 50.0)),#1
                                                ("375",        (375.0, None,  100.0, 50.0)),#2
                                                ("325_scaled", (325.0, 375.0,  86.7, 43.3)),#3
                                                ("275_scaled", (275.0, 325.0,  73.3, 36.7)),#4
                                                ][2:3] )),
                 "triggerList": triggers_ht_eps,
                 }

    def ra1Cosmetics(self) : return False
    
    def calcListJet(self, obj, etRatherThanPt, ptMin, lowPtThreshold, lowPtName, highPtThreshold, highPtName, htThreshold) :
        def calcList(jet, met, photon, muon, electron, muonsInJets, jetIdFlag) :
            outList = [
                calculables.xclean.xcJet(jet,
                                         applyResidualCorrectionsToData = False,
                                         gamma = photon,
                                         gammaDR = 0.5,
                                         muon = muon,
                                         muonDR = 0.5,
                                         correctForMuons = not muonsInJets,
                                         electron = electron,
                                         electronDR = 0.5),
                calculables.jet.Indices( jet, ptMin = ptMin,           etaMax = 3.0, flagName = jetIdFlag),
                calculables.jet.Indices( jet, ptMin = lowPtThreshold,  etaMax = 3.0, flagName = jetIdFlag, extraName = lowPtName),
                calculables.jet.Indices( jet, ptMin = highPtThreshold, etaMax = 3.0, flagName = jetIdFlag, extraName = highPtName),
                
                calculables.jet.SumP4(jet),
                calculables.jet.SumP4(jet, extraName = lowPtName),
                calculables.jet.SumP4(jet, extraName = highPtName),
                calculables.jet.DeltaPhiStar(jet, extraName = lowPtName),
                calculables.jet.DeltaPhiStar(jet),
                calculables.jet.DeltaPseudoJet(jet, etRatherThanPt),
                calculables.jet.AlphaT(jet, etRatherThanPt),
                calculables.jet.AlphaTMet(jet, etRatherThanPt, met),
                calculables.jet.MhtOverMet((jet[0], jet[1]+highPtName), met),
                calculables.jet.deadEcalDR(jet, extraName = lowPtName, minNXtals = 10),
                supy.calculables.other.fixedValue("%sFixedHtBin%s"%jet, htThreshold),
                ]
            return outList+supy.calculables.fromCollections(calculables.jet, [jet])

        outList = calcList(obj["jet"], obj["met"], obj["photon"], obj["muon"], obj["electron"], obj["muonsInJets"], obj["jetId"])
        if all([("comp"+item in obj) for item in ["Jet", "Met","MuonsInJets","JetId"]]) :
            outList += calcList(obj["compJet"], obj["compMet"], obj["photon"], obj["muon"], obj["electron"], obj["compMuonsInJets"], obj["compJetId"])
        return outList

    def calcListOther(self, obj, triggers) :
        return [
            calculables.xclean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.xclean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),

            calculables.muon.Indices( obj["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
            calculables.photon.Indices(obj["photon"],  ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),
            #calculables.photon.Indices(obj["photon"],  ptMin = 25, flagName = "photonIDTightFromTwikiPat"),

            calculables.other.RecHitSumPt(obj["rechit"]),
            calculables.other.RecHitSumP4(obj["rechit"]),
            
            calculables.vertex.ID(),
            calculables.vertex.Indices(),
            calculables.other.lowestUnPrescaledTrigger(triggers),
            ]
    
    def listOfCalculables(self, params) :
        obj = params["objects"]
        outList = []
        outList += supy.calculables.zeroArgs(supy.calculables)
        outList += supy.calculables.zeroArgs(calculables)
        outList += supy.calculables.fromCollections(calculables.muon, [obj["muon"]])
        outList += supy.calculables.fromCollections(calculables.electron, [obj["electron"]])
        outList += supy.calculables.fromCollections(calculables.photon, [obj["photon"]])
        outList += self.calcListOther(obj, params["triggerList"])
        outList += self.calcListJet(obj, params["etRatherThanPt"], params["thresholds"][3],
                                    params["lowPtThreshold"], params["lowPtName"], params["highPtThreshold"], params["highPtName"], params["thresholds"][0])
        return outList
    
    def listOfSteps(self, params) :
        _jet  = params["objects"]["jet"]
        _electron = params["objects"]["electron"]
        _muon = params["objects"]["muon"]
        _photon = params["objects"]["photon"]
        _met  = params["objects"]["met"]
        _etRatherThanPt = params["etRatherThanPt"]
        _et = "Et" if _etRatherThanPt else "Pt"

        scanBefore = [supy.steps.filters.label("scanBefore"), steps.gen.scanHistogrammer(tanBeta = params["tanBeta"])] if params["tanBeta"]!=None else []
        scanAfter = [supy.steps.filters.label("scanAfter"),
                     steps.gen.scanHistogrammer(tanBeta = params["tanBeta"], htVar = "%sSum%s%s"%(_jet[0], _et, _jet[1]))] if params["tanBeta"]!=None else []
        htUpper = [steps.other.variableLessFilter(params["thresholds"][1],"%sSum%s%s"%(_jet[0], _et, _jet[1]), "GeV")] if params["thresholds"][1]!=None else []
        return scanBefore + [
            steps.printer.progressPrinter(),
            steps.trigger.lowestUnPrescaledTriggerFilter().onlyData(),
            steps.trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0").onlyData(),
            
            steps.trigger.physicsDeclaredFilter().onlyData(),
            steps.filters.monster(),
            steps.filters.hbheNoise().onlyData(),

            supy.steps.histos.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin").onlySim(),
            steps.trigger.hltPrescaleHistogrammer(params["triggerList"]).onlyData(),
            
            #steps.other.cutSorter([

            ##when using full scaling
            #steps.jet.htBinFilter(_jet, min = params["htBin"], max = params["htBin"]),
            #steps.jet.jetSelector(_jet, params["thresholds"][2], 0),
            #steps.jet.jetSelector(_jet, params["thresholds"][2], 1),

            #otherwise
            steps.jet.jetPtSelector(_jet, params["thresholds"][2], 0),
            steps.jet.jetPtSelector(_jet, params["thresholds"][2], 1),
            steps.jet.jetEtaSelector(_jet,2.5,0),
            
            #steps.other.iterHistogrammer("ecalDeadTowerTrigPrimP4", 256, 0.0, 128.0, title=";E_{T} of ECAL TP in each dead region (GeV);TPs / bin", funcString="lambda x:x.Et()"),
            supy.steps.histos.multiplicity("vertexIndices"),
            supy.steps.filters.multiplicity("vertexIndices",                  min = 1),
            supy.steps.filters.multiplicity("%sIndices%s"%_muon,              max = 0),
            supy.steps.filters.multiplicity("%sIndices%s"%_electron,          max = 0),
            supy.steps.filters.multiplicity("%sIndices%s"%_photon,            max = 0),
            supy.steps.filters.multiplicity("%sIndicesOther%s"%_jet,          max = 0),
            supy.steps.filters.multiplicity("%sIndicesOther%s"%_muon,         max = 0),
            supy.steps.filters.multiplicity("%sIndicesUnmatched%s"%_electron, max = 0),
            supy.steps.filters.multiplicity("%sIndicesUnmatched%s"%_photon,   max = 0),
            supy.steps.filters.multiplicity("%sIndices%s"%_jet, min = params["nJetsMinMax"][0], max = params["nJetsMinMax"][1]),
            steps.jet.uniquelyMatchedNonisoMuons(_jet), 
            
            supy.steps.histos.histogrammer("%sSum%s%s"%(_jet[0], _et, _jet[1]), 50, 0, 2500, title = ";H_{T} (GeV) from %s%s %ss;events / bin"%(_jet[0], _jet[1], _et)),
            supy.steps.filters.value("%sSum%s%s"%(_jet[0], _et, _jet[1]), min = params["thresholds"][0]),
            ] + htUpper + [
            supy.steps.histos.histogrammer("%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1]+params["highPtName"],_met)),
            supy.steps.filters.value("%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met), max = 1.25),
            
            supy.steps.histos.histogrammer("%sSumP4%s"%_jet, 50, 0, 500, title = ";MHT from %s%s (GeV);events / bin"%_jet, funcString = "lambda x:x.pt()"),
            supy.steps.filters.pt("%sSumP4%s"%_jet, min = 100.0),
            supy.steps.histos.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
            supy.steps.histos.histogrammer("vertexSumPt", 100, 0.0, 1.0e3, title = ";SumPt of 2nd vertex (GeV);events / bin", funcString = "lambda x:([0.0,0.0]+sorted(x))[-2]"),
            #supy.steps.histos.histogrammer("logErrorTooManySeeds",    2, 0.0, 1.0, title = ";logErrorTooManySeeds;events / bin"),
            #supy.steps.histos.histogrammer("logErrorTooManyClusters", 2, 0.0, 1.0, title = ";logErrorTooManyClusters;events / bin"),
            
            #many plots
            steps.trigger.lowestUnPrescaledTriggerHistogrammer().onlyData(),
            supy.steps.filters.label("singleJetPlots1"),
            steps.jet.singleJetHistogrammer(_jet),
            supy.steps.filters.label("jetSumPlots1"), 
            steps.jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            supy.steps.histos.histogrammer("%sDeltaPhiStar%s%s"%(_jet[0], _jet[1], params["lowPtName"]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            supy.steps.histos.histogrammer("%sDeltaPhiStar%s"%(_jet[0], _jet[1]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            supy.steps.histos.histogrammer(_met,100,0.0,500.0,title=";"+_met+" (GeV);events / bin", funcString = "lambda x: x.pt()"),
            supy.steps.filters.label("kinematicPlots1"),

            steps.jet.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            steps.other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            steps.jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            steps.jet.alphaHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt),
            #steps.jet.alphaMetHistogrammer(cs = _jet, deltaPhiStarExtraName = params["lowPtName"], etRatherThanPt = _etRatherThanPt, metName = _met),

            #signal selection
            #supy.steps.filters.pt("%sSumP4%s"%_jet, min = 140.0),
            supy.steps.filters.value("%sAlphaT%s%s"%(_jet[0],"Et" if _etRatherThanPt else "Pt",_jet[1]), min = 0.55),
            #]), #end cutSorter

            #steps.Trigger.lowestUnPrescaledTriggerFilter(),
            #steps.Trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            #
            #steps.Trigger.physicsDeclaredFilter(),
            #steps.other.monsterEventFilter(),
            #steps.other.hbheNoiseFilter(),
            #
            #steps.other.variableLessFilter(1.25,"%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met)),
            #steps.other.deadEcalFilter(jets = _jet, extraName = params["lowPtName"], dR = 0.3, dPhiStarCut = 0.5),
            
            
            supy.steps.histos.histogrammer("vertexIndices", 20, -0.5, 19.5, title=";N vertices;events / bin", funcString="lambda x:len(x)"),
            supy.steps.histos.histogrammer("%sIndices%s"%_jet, 20, -0.5, 19.5, title=";number of %s%s passing ID#semicolon p_{T}#semicolon #eta cuts;events / bin"%_jet, funcString="lambda x:len(x)"),
            steps.jet.cleanJetHtMhtHistogrammer(_jet,_etRatherThanPt),
            supy.steps.histos.histogrammer("%sDeltaPhiStar%s%s"%(_jet[0], _jet[1], params["lowPtName"]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            supy.steps.histos.histogrammer("%sDeltaPhiStar%s"%(_jet[0], _jet[1]), 20, 0.0, r.TMath.Pi(), title = ";#Delta#phi*;events / bin", funcString = 'lambda x:x[0][0]'),
            supy.steps.histos.histogrammer("%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met), 100, 0.0, 3.0,
                                     title = ";MHT %s%s / %s;events / bin"%(_jet[0],_jet[1]+params["highPtName"],_met)),

            supy.steps.histos.histogrammer("%sRecHitSumPt"%params["objects"]["rechit"], 30, 0, 300, title = ";Sum of HBHE (sev.#geq10), EB,EE (sev.#geq2) RecHit p_{T} (GeV);events / bin"),
            supy.steps.filters.value("%sRecHitSumPt"%params["objects"]["rechit"], max = 30.0),
            
            #steps.other.skimmer(),
            #steps.other.duplicateEventCheck(),
            #steps.other.cutBitHistogrammer(self.togglePfJet(_jet), self.togglePfMet(_met)),
            #steps.Print.eventPrinter(),
            #steps.Print.jetPrinter(_jet),

            #steps.Print.particleP4Printer(_muon),
            #steps.Print.particleP4Printer(_photon),
            #steps.Print.recHitPrinter("clusterPF","Ecal"),
            #steps.Print.htMhtPrinter(_jet),
            #steps.Print.alphaTPrinter(_jet,_etRatherThanPt),
            #steps.Gen.genParticlePrinter(minPt = 10.0, minStatus = 3),
                   
            #steps.other.pickEventSpecMaker(),
            #steps.Displayer.displayer(jets = _jet,
            #                          muons = _muon,
            #                          met       = params["objects"]["met"],
            #                          electrons = params["objects"]["electron"],
            #                          photons   = params["objects"]["photon"],                            
            #                          recHits   = params["objects"]["rechit"], recHitPtThreshold = 1.0,#GeV
            #                          scale = 400.0,#GeV
            #                          etRatherThanPt = _etRatherThanPt,
            #                          deltaPhiStarExtraName = params["lowPtName"],
            #                          deltaPhiStarCut = 0.5,
            #                          deltaPhiStarDR = 0.3,
            #                          j2Factor = params["thresholds"][2]/params["thresholds"][0],
            #                          mhtOverMetName = "%sMht%sOver%s"%(_jet[0],_jet[1]+params["highPtName"],_met),
            #                          metOtherAlgo  = params["objects"]["compMet"],
            #                          jetsOtherAlgo = params["objects"]["compJet"],
            #                          #doGenJets = True,
            #                          markusMode = False,
            #                          ),
            ] + scanAfter + [supy.steps.filters.value("%sSumEt%s"%_jet, min = bin) for bin in [475, 575, 675, 775, 875]]
    
    def listOfSampleDictionaries(self) :
        return [samples.ht, samples.jetmet, samples.mc, samples.top]

    def listOfSamples(self,params) :
        from supy.samples import specify

        def data() :
            out = []

            #2011
            jwPrompt = calculables.other.jsonWeight("cert/Cert_160404-178677_7TeV_PromptReco_Collisions11_JSON.sub.txt")
            jwMay = calculables.other.jsonWeight("cert/Cert_160404-163869_7TeV_May10ReReco_Collisions11_JSON_v3.txt")
            jwAug = calculables.other.jsonWeight("cert/Cert_170249-172619_7TeV_ReReco5Aug_Collisions11_JSON_v3.txt")
            
            out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.job536", weights = jwMay   , overrideLumi = 204.4)
            out += specify(names = "HT.Run2011A-05Aug2011-v1.AOD.job528",   weights = jwAug   , overrideLumi = 355.4)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.job535",  weights = jwPrompt, overrideLumi = 730.6)
            out += specify(names = "HT.Run2011A-PromptReco-v6.AOD.job527",  weights = jwPrompt, overrideLumi = 640.2)
            out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.job515",  weights = jwPrompt, overrideLumi = 200.7)
            out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.job519",  weights = jwPrompt, overrideLumi = 257.3)
            out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.job531",  weights = jwPrompt, overrideLumi = 248.7)
            #out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.job533",  weights = jwPrompt, overrideLumi =  99.0) #need to investigate triggers
            #out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.job564",  weights = jwPrompt, overrideLumi = 362.6)
            ##out += specify(names = "HT.Run2011B-PromptReco-v1.AOD.job592",  weights = jwPrompt, overrideLumi =   0.0)

            #out = specify(names = "calo_375")
            return out

        def dataEps() :
            out = []

            jw = calculables.other.jsonWeight("cert/Cert_160404-167913_7TeV_PromptReco_Collisions11_JSON.txt") #1078/pb            

            out += specify(names = "HT.Run2011A-May10ReReco-v1.AOD.Bryn",   weights = jw, overrideLumi = 183.0)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn1",   weights = jw, overrideLumi =  70.2)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn2",   weights = jw, overrideLumi = 101.3)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Bryn3",   weights = jw, overrideLumi =  74.8)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren1", weights = jw, overrideLumi = 181.2)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren2", weights = jw, overrideLumi = 122.8)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren3", weights = jw, overrideLumi =  36.4)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren4", weights = jw, overrideLumi =  50.5)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren5", weights = jw, overrideLumi = 130.6)
            out += specify(names = "HT.Run2011A-PromptReco-v4.AOD.Darren6", weights = jw, overrideLumi = 116.0)

            #out += specify(names = "HT_skim")
            #out += specify(names = "MT2_events")
            #out += specify(names = "qcd_py6_375")
            #out += specify(names = "calo_375")
            return out

        def qcd_py6(eL) :
            q6 = [0,5,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q6.index(80)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py6_pt_%d_%d"%t)[:None if t[1] else -2] for t in zip(q6,q6[1:]+[0])[iCut:]] )

        def g_jets_py6(eL) :
            return specify( effectiveLumi = eL, color = r.kGreen,
                            names = ["v12_g_jets_py6_pt%d"%t for t in [30,80,170]] )

        def qcd_py8(eL) :
            q8 = [0,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q8.index(50)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("v14_qcd_py8_pt%dto%d"%t)[:None if t[1] else -3] for t in zip(q8,q8[1:]+[0])[iCut:]] )

        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000]]
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])

        def g_jets_mg(eL) :
            gM = [40,100,200]
            return specify( effectiveLumi = eL, color = r.kGreen,
                            names = [("g_jets_mg_ht_%d_%d")[:None if t[1] else -2] for t in zip(gM,gM[1:]+["inf"])] )

        def ttbar_mg(eL, era = "") :
            names = ""
            if era=="spring11" : names = "tt_tauola_mg"
            if era=="summer11" : names = "tt_jets_mg_tauola_summer11"
            return specify( names = names, effectiveLumi = eL, color = r.kOrange)

        def top_ph(eL) :
            return specify( names = self.singleTopList(), effectiveLumi = eL, color = r.kOrange-7)
            
        def ewk(eL, era = "") :
            zName = ""
            wName = ""
            if era=="spring11" :
                zName = "zinv_jets_mg"
                wName = "w_jets_mg"
            if era=="summer11" :
                zName = "znunu_jets_mg_ht_200_inf_summer11_skim"
                wName = "w_jets_mg_tauola_ht_300_inf_summer11"
            
            return ( specify(names = zName,  effectiveLumi = eL, color = r.kRed + 1) +
                     #specify(names = "z_jets_mg_v12_skim", effectiveLumi = eL, color = r.kYellow-3) +
                     specify(names = wName, effectiveLumi = eL, color = 28         ) )

        def susy(eL) :
            return specify(names = "lm6", effectiveLumi = eL, color = r.kRed-1) + specify(names = "lm4", effectiveLumi = eL, color = r.kRed-2)

        def scan(tanBeta) :
            return specify(names = "scan_tanbeta%d"%tanBeta, color = r.kMagenta, nFilesMax = 1)
                     
        qcd_func,g_jets_func = {"py6": (qcd_py6,g_jets_py6),
                                "py8": (qcd_py8,g_jets_py6), # no g_jets_py8 available
                                "mg" : (qcd_mg, g_jets_mg ) }[params["mcSoup"]]
        era = "spring11"
        #era = "summer11"
        smLumi = 30000 # 1/pb
        susyLumi = 60000
        #return data()
        return ( dataEps() +
                 qcd_func(smLumi) + #g_jets_func(eL) +
                 top_ph(smLumi) +
                 ttbar_mg(smLumi, era = era) + ewk(smLumi, era = era) +
                 susy(susyLumi)
                 ) if params["tanBeta"]==None else scan(params["tanBeta"])

    def singleTopList(self) :
        return ["top_s_ph", "top_t_ph", "top_tW_ph", "tbar_s_ph", "tbar_t_ph", "tbar_tW_ph"]

    def mergeSamples(self, org) :
        def md(x, y) :
            x.update(y)
            return x
        
        org.mergeSamples(targetSpec = {"name":"2011 Data", "color":r.kBlack, "markerStyle":20}, allWithPrefix = "HT.Run2011")

        mcOps = {"markerStyle":1, "lineWidth":3, "goptions":"hist"}
        if "pythia6"  in org.tag :
            org.mergeSamples(targetSpec = md({"name":"QCD Multijet", "color":r.kGreen+3}, mcOps), allWithPrefix = "qcd_py6")
        org.mergeSamples(targetSpec = md({"name":"tt", "color": r.kBlue}, mcOps), allWithPrefix = "tt")
        org.mergeSamples(targetSpec = md({"name":"t",  "color": r.kOrange-7}, mcOps), sources = self.singleTopList())
        org.mergeSamples(targetSpec = md({"name":"Z + jets", "color": r.kRed+1}, mcOps), allWithPrefix = "z")
        org.mergeSamples(targetSpec = md({"name":"W + jets", "color": r.kOrange-3}, mcOps), allWithPrefix = "w_jets")
        org.mergeSamples(targetSpec = md({"name":"LM6", "color":r.kMagenta}, mcOps), allWithPrefix = "lm6")
        ewkSources = ["tt", "Z + jets", "W + jets"]
        qcdSources = ["QCD Multijet"]

        if not self.ra1Cosmetics() :
            org.mergeSamples(targetSpec = md({"name":"Standard Model ", "color":r.kAzure+6}, mcOps), sources = ewkSources + qcdSources, keepSources = True)
        else :
            ewk = "t#bar{t}, W, Z + Jets"
            org.mergeSamples(targetSpec = md({"name":ewk, "color":r.kBlue}, mcOps), sources = ewkSources)
            org.mergeSamples(targetSpec = md({"name":"Standard Model ", "color":r.kAzure+6}, mcOps), sources = qcdSources + [ewk], keepSources = True)

    def conclude(self, conf) :
        org = self.organizer(conf)
        ##for skimming only
        #utils.printSkimResults(org)            

        self.mergeSamples(org)
        org.scale() if not self.parameters()["tanBeta"] else org.scale(100.0)
        
        self.makeStandardPlots(org)
        #self.makeIndividualPlots(org)

    def makeStandardPlots(self, org) :
        #plot
        pl = supy.plotter(org,
                          pdfFileName = self.pdfFileName(org.tag),
                          samplesForRatios = ("2011 Data","Standard Model "),
                          sampleLabelsForRatios = ("data","s.m."),
                          printRatios = True,
                          showStatBox = not self.ra1Cosmetics(),
                          rowColors = [r.kBlack, r.kViolet+4],
                          #whiteList = ["lowestUnPrescaledTrigger"],
                          #doLog = False,
                          #compactOutput = True,
                          #noSci = True,
                          #latexYieldTable = True,
                          linYAfter = ("value", "0.55<=xcak5JetAlphaTEtPat"),
                          pegMinimum = 0.1,
                          blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                          )
        pl.plotAll()
        #self.makeEfficiencyPlots(org, tag, sampleName = "LM1")

    def makeIndividualPlots(self, org) :
        #plot all
        pl = supy.plotter(org,
                          pdfFileName = self.pdfFileName(org.tag),
                          showStatBox = False,
                          doLog = True,
                          pegMinimum = 0.1,
                          anMode = True,
                          )
        pl.individualPlots(plotSpecs = [{"plotName":"xcak5JetAlphaTRoughPat",
                                         "stepName" :"alphaHistogrammer",
                                         "stepDesc" :"xcak5JetPat",
                                         "newTitle":";#alpha_{T};events / bin",
                                         "legendCoords": (0.55, 0.60, 0.85, 0.90),
                                         "stampCoords": (0.75, 0.55)
                                         },
                                        {"plotName":"jetMultiplicity",
                                         "stepName":"singleJetHistogrammer",
                                         "stepDesc":"xcak5JetPat through index 2",
                                         "newTitle":";N_{jets};events / bin",
                                         "legendCoords": (0.7, 0.7, 0.92, 0.92),
                                         "stampCoords": (0.5, 0.28),
                                         },
                                        {"plotName":"xcak5JetHtPat",
                                         "stepName":"cleanJetHtMhtHistogrammer",
                                         "stepDesc":"xcak5JetPat",
                                         "newTitle":";H_{T} (GeV);events / bin",
                                         "legendCoords": (0.6, 0.60, 0.92, 0.92),
                                         "stampCoords": (0.45, 0.88)
                                        },
                                        ##after alphaT
                                        {"plotName":"xcak5JetDeltaPhiStarPat",
                                         "stepName":"histogrammer",
                                         "stepDesc" :"(lambda x:x[0][0])(xcak5JetDeltaPhiStarPat)",
                                         "index" : -1,
                                         "newTitle":";#Delta#phi*;events / bin",
                                         "legendCoords": (0.6, 0.6, 0.92, 0.92),
                                         "stampCoords": (0.33, 0.88),
                                         },
                                        {"plotName":"xcak5JetHtPlusMhtRoughPat",
                                         "stepName":"cleanJetHtMhtHistogrammer",
                                         "stepDesc":"xcak5JetPat",
                                         "index":-1,
                                         "newTitle":";M_{eff} (GeV);events / bin",
                                         "legendCoords": (0.7, 0.7, 0.92, 0.92),
                                         "stampCoords": (0.75, 0.4),
                                         },
                                        {"plotName":"xcak5JetIndicesPat",
                                         "stepName":"histogrammer",
                                         "stepDesc" :"(lambda x:len(x))(xcak5JetIndicesPat)",
                                         "index" : -1,
                                         "newTitle":";N_{jets};events / bin",
                                         "legendCoords": (0.6, 0.6, 0.92, 0.92),
                                         "stampCoords": (0.6, 0.38),
                                         }
                                        ],
                           newSampleNames = None,
                           #newSampleNames = {"qcd_mg_nVtx": "Madgraph QCD",
                           #                  "g_jets_mg_nVtx": "Madgraph #gamma + jets",
                           #                  "2011 Data": "Data",
                           #                  "standard_model_nVtx": "Standard Model",
                           #                  },
                           preliminary = True,
                           )


    def makeEfficiencyPlots(self, org, tag, sampleName) :
        def sampleIndex(org, name) :
            for iSample,sample in enumerate(org.samples) :
                if sample["name"]==name : return iSample
            assert False, "could not find sample %s"%name

        def numerAndDenom(org, var) :
            d = {}
            for selection in org.selections :
                if selection.name!= "passFilter" : continue
                if   "htLabel1" in selection.title : label = "before"
                elif "htLabel2" in selection.title : label = "after"
                else : continue
                if var in selection :
                    d[label] = selection[var][sampleIndex(org, sampleName)].Clone(label)
                
            return d

        keep = []
        canvas = r.TCanvas()
        canvas.SetRightMargin(0.2)
        canvas.SetTickx()
        canvas.SetTicky()
        psFileName = "%s.ps"%tag
        canvas.Print(psFileName+"[","Lanscape")

        assert len(self.parameters()["objects"])==1
        for key,value in self.parameters()["objects"].iteritems() :
            jet = value["jet"]

        for variable in ["%sSumEt%s"%jet] :
            histos = numerAndDenom(org, variable)
            if "before" not in histos or "after" not in histos : continue
            result = histos["after"].Clone(variable)
            result.Scale(1.0/histos["before"].Integral(0, histos["before"].GetNbinsX()+1))
            result.SetMarkerStyle(20)
            result.SetStats(False)
            if result.ClassName()[2]=="1" :
                #result.GetYaxis().SetRangeUser(0.0,1.0)
                result.GetYaxis().SetTitle("efficiency")
                result.Draw()
            else :
                #result.GetZaxis().SetRangeUser(0.0,1.0)
                result.GetZaxis().SetTitle("efficiency")
                result.Draw("colz")
            canvas.Print(psFileName,"Lanscape")

        canvas.Print(psFileName+"]","Lanscape")                
        os.system("ps2pdf "+psFileName)
        os.remove(psFileName)

