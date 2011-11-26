import supy,steps,calculables,samples,ROOT as r

class triggers(supy.analysis) :
    def parameters(self) :
        return { "muon" : self.vary({"pf" : ("muon","PF"),
                                     #"pat" : ("muon","Pat")
                                     }),
                 "electron":("electron","PF") }
    
    def listOfCalculables(self, pars) :
        outList  = supy.calculables.zeroArgs(supy.calculables)
        outList += supy.calculables.fromCollections(calculables.muon, [pars["muon"]])
        outList += supy.calculables.fromCollections(calculables.electron, [pars["electron"]])
        outList +=[calculables.muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                   calculables.muon.IndicesAnyIsoIsoOrder(pars['muon'], "CombinedRelativeIso"),
                   calculables.muon.LeadingIsoAny(pars['muon'], ptMin = 18, iso = "CombinedRelativeIso"),
                   calculables.electron.Indices( pars["electron"], ptMin = 10, simpleEleID = "95", useCombinedIso = True),
                   calculables.other.PtSorted(pars['muon'])
                   ]
        
        return outList
    
    def listOfSteps(self, pars) :
        return (
            [supy.steps.printer.progressPrinter(),
             supy.steps.histos.value("%sPtSorted%s"%pars['muon'], 2,0,1),
             #supy.steps.filters.absEta("%sP4%s"%pars['muon'], max = 2.1, indices = "%sIndicesAnyIso%s"%pars['muon'], index = 0),
             steps.trigger.triggerScan( pattern = r"HLT_Mu\d*(_eta2p1)?_v\d", prescaleRequirement = "prescale==1", tag = "Mu"),
             steps.trigger.triggerScan( pattern = r"HLT_Mu\d*(_eta2p1)?_v\d", prescaleRequirement = "True", tag = "MuAll"),
             #steps.trigger.triggerScan( pattern = r"HLT_Ele\d*", prescaleRequirement = "prescale==1", tag = "Ele"),
             #steps.trigger.triggerScan( pattern = r"HLT_HT\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "HT"),
             #steps.trigger.triggerScan( pattern = r"HLT_Jet\d*U($|_v\d*)", prescaleRequirement = "prescale==1", tag = "Jet"),
             steps.trigger.hltTurnOnHistogrammer( "%sLeadingPtAny%s"%pars["muon"], (100,0,50), "HLT_Mu30_v3",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(24,3),(24,4)]]),
             #steps.trigger.hltTurnOnHistogrammer( "%sLeadingPtAny%s"%pars["muon"], (80,0,40), "HLT_Mu30_v4",["HLT_Mu%d_v%d"%d for d in [(20,2),(20,1),(24,3),(24,4)]]),
             #steps.filters.pt("%sP4%s"%pars['muon'], min = 18, indices = "%sIndicesAnyIso%s"%pars['muon'], index = 0),
             #steps.trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v10",["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #steps.trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v9" ,["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #steps.trigger.hltTurnOnHistogrammer( "%sLeadingIsoAny%s"%pars["muon"],(100,0,1), "HLT_IsoMu17_v8" ,["HLT_Mu%d_v%d"%d for d in [(12,3),(12,4),(15,4),(15,5)]]),
             #steps.trigger.hltTurnOnHistogrammer( "%sLeadingPt%s"%pars["muon"], (50,0,25), "HLT_Mu15_v1",["HLT_Mu%d"%d for d in [9,7,5,3]]),
             supy.steps.filters.multiplicity("%sPt%s"%pars['muon'], min = 2),
             supy.steps.histos.value("%sPtSorted%s"%pars['muon'], 2,0,1),
             ])
    
    def listOfSampleDictionaries(self) : return [samples.muon,samples.jetmet,samples.electron]

    def listOfSamples(self,pars) :
        return ( supy.samples.specify(names = "SingleMu.2011B-PR1.1b", color = r.kOrange) +
                 supy.samples.specify(names = "SingleMu.2011B-PR1.1a", color = r.kViolet) +
                 supy.samples.specify(names = "SingleMu.2011A-Oct.1", color = r.kBlue,) +
                 supy.samples.specify(names = "SingleMu.2011A-Aug.1", color = r.kGreen) +
                 supy.samples.specify(names = "SingleMu.2011A-PR4.1", color = r.kBlack) +
                 supy.samples.specify(names = "SingleMu.2011A-May.1", color = r.kRed ) +
                 [])
        

    def conclude(self,pars) :
        org = self.organizer(pars)
        #org.mergeSamples(targetSpec = {"name":"SingleMu", "color":r.kBlack}, allWithPrefix="SingleMu")
        #org.scale()
        
        supy.plotter(org,
                     psFileName = self.psFileName(org.tag),
                     #samplesForRatios = ("2010 Data","standard_model"),
                     #sampleLabelsForRatios = ("data","s.m."),
                     #whiteList = ["lowestUnPrescaledTrigger"],
                     #doLog = False,
                     #compactOutput = True,
                     #noSci = True,
                     #pegMinimum = 0.1,
                     blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                     ).plotAll()
