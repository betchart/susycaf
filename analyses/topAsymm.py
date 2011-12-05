import supy,steps,calculables,samples
import os,math,copy,ROOT as r, numpy as np

class topAsymm(supy.analysis) :
    ########################################################################################

    @staticmethod
    def mutriggers(self) :             # L1 prescaling evidence
        ptv = { 12   :(1,2,3,4,5),     # 7,8,11,12
                15   :(2,3,4,5,6,8,9), # 12,13
                20   :(1,2,3,4,5,7,8),
                24   :(1,2,3,4,5,7,8,11,12),
                24.21:(1,),
                30   :(1,2,3,4,5,7,8,11,12),
                30.21:(1,),
                40   :(1,2,3,5,6,9,10),
                40.21:(1,4,5),
                }
        return sum([[("HLT_Mu%d%s_v%d"%(int(pt),"_eta2p1" if type(pt)!=int else "",v),int(pt)+1) for v in vs] for pt,vs in sorted(ptv.iteritems())],[])

    @staticmethod
    def unreliableTriggers(self) :
        '''Evidence of L1 prescaling at these ostensible prescale values'''
        return { "HLT_Mu15_v9":(25,65),
                 "HLT_Mu20_v8":(30,),
                 "HLT_Mu24_v8":(20,25),
                 "HLT_Mu24_v11":(35,),
                 "HLT_Mu24_v12":(35,),
                 "HLT_Mu30_v8":(4,10),
                 "HLT_Mu30_v11":(4,20),
                 "HLT_Mu30_v12":(8,20),
                 "HLT_Mu40_v6":(4,),
                 "HLT_Mu40_v9":(10,),
                 "HLT_Mu40_v10":(10,)
                 }

    def parameters(self) :

        objects = self.vary()
        fields =                           [ "jet",               "met",           "sumP4",    "sumPt",       "muon",         "electron",         "photon",         "muonsInJets"]
        objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"), "metP4PF",       "pfSumP4",  "metSumEtPF",  ("muon","PF"),  ("electron","PF"),  ("photon","Pat"),  True]))
        #objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),  "metP4AK5TypeII", "xcSumP4", "xcSumPt",     ("muon","Pat"), ("electron","Pat"), ("photon","Pat"),  False]))

        leptons = self.vary()
        fieldsLepton    =                            ["name","ptMin", "etaMax",              "isoVar", "triggers"]
        leptons["muon"]     = dict(zip(fieldsLepton, ["muon",     20,     2.1, "CombinedRelativeIso",   mutriggers()]))
        #leptons["electron"] = dict(zip(fieldsLepton, ["electron", 30,       9,         "IsoCombined", ("FIX","ME")]))
        
        bVar = "NTrkHiEff" # "TrkCountingHighEffBJetTags"
        bCut = {"normal"   : {"index":1, "min":2.0},
                "inverted" : {"index":1, "max":2.0}}
        lIso = {"normal":  {"N":1, "indices":"Indices"},
                "inverted":{"N":0, "indices":"IndicesNonIso"}}

        return { "objects": objects,
                 "lepton" : leptons,
                 "nJets" :  {"min":4,"max":None},
                 "nJets2" : {"min":4,"max":None},
                 "bVar" : bVar,
                 "selection" : self.vary({"top" : {"bCut":bCut["normal"],  "lIso":lIso["normal"]},
                                          #"Wlv" : {"bCut":bCut["inverted"],"lIso":lIso["normal"]},
                                          "QCD" : {"bCut":bCut["normal"],  "lIso":lIso["inverted"]}
                                          }),
                 "topBsamples": { "pythia"   : ("tt_tauola_fj",["tt_tauola_fj.wNonQQbar.tw.nvr",
                                                              "tt_tauola_fj.wTopAsymP00.tw.nvr"
                                                              ]),
                                "madgraph" : ("FIXME",[]),
                                }["pythia"]
                 }
    ########################################################################################

    def listOfSampleDictionaries(self) : return [samples.mc, samples.muon]

    def listOfSamples(self,pars) :
        from supy.samples import specify

        def data( ) :
            return ( supy.samples.specify( names = ['SingleMu.2011B-PR1.1b',
                                                    'SingleMu.2011B-PR1.1a',
                                                    'SingleMu.2011A-Oct.1',
                                                    'SingleMu.2011A-Aug.1',
                                                    'SingleMu.2011A-PR4.1',
                                                    'SingleMu.2011A-May.1'], weights = 'tw') +
        def qcd_py6_mu(eL = None) :
            q6 = [0,5,15,20,30,50,80,120,150,None]
            iCut = q6.index(15)
            return specify( effectiveLumi = eL, weights = ['tw','nvr'],
                            names = ["qcd_py6fjmu_pt_%s"%("%d_%d"%(low,high) if high else "%d"%low) for low,high in zip(q6[:-1],q6[1:])[iCut:]] )  if "Wlv" not in pars['tag'] else []
        def qcd_mg(eL = None) :
            qM = ["%d"%t for t in [50,100,250,500,1000][1:]]
            return specify( effectiveLumi = eL, color = r.kBlue, weights = ['tw','nvr'],
                            names = ["qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])]) if "Wlv" not in pars['tag'] else []
        def ttbar_mg(eL = None) :
            return (specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kBlue, weights = ['wNonQQbar','tw','nvr']) +
                    sum([specify( names = "tt_tauola_mg", effectiveLumi = eL, color = color, weights = [calculables.top.wTopAsym( asym, R_sm = -0.05), 'nvr' ])
                         for asym,color in [(0.0,r.kOrange),(-0.3,r.kGreen),(0.3,r.kRed)]], [])
                    )[: 0 if "QCD" in pars['tag'] else 2 if 'Wlv' in pars['tag'] else None]
        def ttbar_py(eL = None) :
            return (specify(names = "tt_tauola_fj", effectiveLumi = eL, color = r.kBlue, weights = ["wNonQQbar",'tw','nvr']) +
                    sum( [specify(names = "tt_tauola_fj", effectiveLumi = eL, color = color, weights = [ calculables.top.wTopAsym(asym), 'tw','nvr' ] )
                          for asym,color in [(0.0,r.kOrange),
                                             (-0.3,r.kGreen),(0.3,r.kRed),
                                             #(-0.6,r.kYellow),(0.6,r.kYellow),
                                             #(-0.5,r.kYellow),(0.5,r.kYellow),
                                             #(-0.4,r.kYellow),(0.4,r.kYellow),
                                             #(-0.2,r.kYellow),(0.2,r.kYellow),
                                             #(-0.1,r.kYellow),(0.1,r.kYellow),
                                             ]], [])
                    )[: 0 if "QCD" in pars['tag'] else 2 if 'Wlv' in pars['tag'] else None]
        def ewk(eL = None) :
            return specify( names = "w_jets_fj_mg", effectiveLumi = eL, color = 28, weights = ['tw','nvr'] ) if "QCD" not in pars['tag'] else []

        return  ( data() + qcd_py6_mu() + ewk() + ttbar_py() )


    ########################################################################################
    def listOfCalculables(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        calcs  = supy.calculables.zeroArgs(supy.calculables)
        calcs += supy.calculables.zeroArgs(calculables)
        calcs += supy.calculables.fromCollections(calculables.muon, [obj["muon"]])
        calcs += supy.calculables.fromCollections(calculables.electron, [obj["electron"]])
        calcs += supy.calculables.fromCollections(calculables.photon, [obj["photon"]])
        calcs += supy.calculables.fromCollections(calculables.jet, [obj["jet"]])
        calcs += [
            calculables.jet.IndicesBtagged(obj["jet"],pars["bVar"]),
            calculables.jet.Indices(      obj["jet"],      ptMin = 20, etaMax = 3.5, flagName = "JetIDloose"),
            calculables.muon.Indices(     obj["muon"],     ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.muon.IndicesTriggering(obj["muon"]),
            calculables.electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "80", useCombinedIso = True),
            calculables.photon.Indices(   obj["photon"],   ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),

            calculables.xclean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.xclean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),
            calculables.xclean.xcJet(obj["jet"], applyResidualCorrectionsToData = False,
                                     gamma    = obj["photon"],      gammaDR = 0.5,
                                     electron = obj["electron"], electronDR = 0.5,
                                     muon     = obj["muon"],         muonDR = 0.5, correctForMuons = not obj["muonsInJets"]),
            calculables.xclean.SumP4(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),
            calculables.xclean.SumPt(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),

            calculables.vertex.ID(),
            calculables.vertex.Indices(),
            calculables.other.lowestUnPrescaledTrigger(zip(*pars["lepton"]["triggers"])[0]),

            calculables.top.mixedSumP4(transverse = obj["met"], longitudinal = obj["sumP4"]),
            calculables.other.pt("mixedSumP4"),
            calculables.top.SemileptonicTopIndex(lepton),            
            calculables.top.fitTopLeptonCharge(lepton),
            calculables.top.TopReconstruction(lepton,obj["jet"],"mixedSumP4"),
            
            calculables.other.Mt(lepton,"mixedSumP4", allowNonIso=True, isSumP4=True),
            calculables.muon.IndicesAnyIsoIsoOrder(obj[pars["lepton"]["name"]], pars["lepton"]["isoVar"]),
            calculables.other.PtSorted(obj['muon']),
            calculables.other.Covariance(('met','PF')),
            supy.calculables.other.abbreviation( "TrkCountingHighEffBJetTags", "NTrkHiEff", fixes = calculables.jet.xcStrip(obj['jet']) ),
            supy.calculables.other.abbreviation( "nVertexRatio", "nvr" ),
            supy.calculables.other.abbreviation('muonTriggerWeightPF','tw'),
            calculables.jet.pt( obj['jet'], index = 0, Btagged = True ),
            calculables.jet.absEta( obj['jet'], index = 3, Btagged = False)
            ]
        calcs += supy.calculables.fromCollections(calculables.top,[('genTop',""),('fitTop',"")])
        calcs.append( calculables.top.TopComboQQBBLikelihood(pars['objects']['jet'], pars['bVar']))
        calcs.append( calculables.top.OtherJetsLikelihood(pars['objects']['jet'], pars['bVar']))
        calcs.append( calculables.top.TopRatherThanWProbability(priorTop=0.5) )
        calcs.append( calculables.other.TriDiscriminant(LR = "DiscriminantWQCD", LC = "DiscriminantTopW", RC = "DiscriminantTopQCD") )
        calcs.append( calculables.other.KarlsruheDiscriminant(pars['objects']['jet'], pars['objects']['met']) )
        calcs.append( supy.calculables.size("%sIndices%s"%pars['objects']['jet']))
        calcs.append( calculables.top.RadiativeCoherence(('fitTop',''),pars['objects']['jet']))
        return calcs
    ########################################################################################

    @staticmethod
    def dataCleanupSteps(pars) :
        obj = pars['objects']
        return ([
            steps.filters.hbheNoise(),
            steps.trigger.physicsDeclaredFilter(),
            steps.filters.monster(),
            steps.trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.trigger.hltPrescaleHistogrammer(zip(*pars['lepton']['triggers'])[0]),
            steps.trigger.lowestUnPrescaledTriggerHistogrammer(),
            supy.steps.histos.multiplicity("vertexIndices", max=15),
            supy.steps.histos.value("%sPtSorted%s"%obj['muon'], 2,-0.5,1.5),
            supy.steps.filters.multiplicity("vertexIndices",min=1),
            ])

    @staticmethod
    def xcleanSteps(pars) :
        obj = pars['objects']
        return ([
            supy.steps.filters.multiplicity(s, max = 0) for s in ["%sIndices%s"%obj["photon"],
                                                                  "%sIndicesUnmatched%s"%obj["photon"],
                                                                  "%sIndices%s"%(obj["electron" if pars["lepton"]["name"]=="muon" else "muon"]),
                                                                  "%sIndicesUnmatched%s"%obj["electron"],
                                                                  "%sIndicesOther%s"%obj["muon"],
                                                                  ]]+[
            steps.jet.forwardFailedJetVeto( obj["jet"], ptAbove = 50, etaAbove = 3.5),
            steps.jet.uniquelyMatchedNonisoMuons(obj["jet"]),
            ])

    @staticmethod
    def selectionSteps(pars, withPlots = True) :
        obj = pars["objects"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.jet.xcStrip(obj["jet"])
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        lEtaMax = pars["lepton"]["etaMax"]
        lIsoIndices = ("%s"+pars["selection"]["lIso"]["indices"]+"%s")%lepton

        topTag = pars['tag'].replace("Wlv","top").replace("QCD","top")
        selections = (
            [supy.steps.histos.multiplicity("%sIndices%s"%obj["jet"]),
             supy.steps.filters.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets"]),
             
             supy.steps.histos.pt("mixedSumP4",100,0,300),
             supy.steps.filters.pt("mixedSumP4",min=20),
             
             self.lepIso(1,pars),
             supy.steps.filters.multiplicity("%sIndices%s"%lepton, max = 1), # drell-yann rejection
             self.lepIso(0,pars),

             supy.steps.filters.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, max = 1.0, indices = lIsoIndices, index = 0),
             supy.steps.filters.multiplicity("%sIndices%s"%lepton, min=pars["selection"]["lIso"]["N"],max=pars["selection"]["lIso"]["N"]),
             supy.steps.filters.pt("%sP4%s"%lepton, min = lPtMin, indices = lIsoIndices, index = 0),
             supy.steps.filters.absEta("%sP4%s"%lepton, max = lEtaMax, indices = lIsoIndices, index = 0),
             
             ]+[supy.steps.histos.value(bVar, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = i) for i in range(3)]+[
            calculables.jet.ProbabilityGivenBQN(obj["jet"], pars['bVar'], binning=(64,-1,15), samples = pars['topBsamples'], tag = topTag),
            supy.steps.histos.value("TopRatherThanWProbability", 100,0,1),
            #supy.steps.filters.value("TopRatherThanWProbability", min = 0.2),
            supy.steps.filters.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1, min = 0.0),
            supy.steps.filters.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], **pars["selection"]["bCut"]),
            ])
        return [s for s in selections if withPlots or s.isSelector or issubclass(type(s),supy.calculables.secondary)]

    @staticmethod
    def lepIso(index,pars) :
        lepton = pars["objects"][pars["lepton"]["name"]]
        return supy.steps.histos.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, 55,0,1.1, indices = "%sIndicesAnyIsoIsoOrder%s"%lepton, index=index)

    def listOfSteps(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        lEtaMax = pars["lepton"]["etaMax"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.jet.xcStrip(obj["jet"])

        return ([
            supy.steps.printer.progressPrinter(),
            supy.steps.histos.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            ] + self.dataCleanupSteps(pars) + [
            calculables.trigger.TriggerWeight(samples = ['SingleMu.Run2011A-PR-v4.FJ.Burt.tw','SingleMu.Run2011A-May10-v1.FJ.Burt.tw'],
                                              triggers = zip(*pars['lepton']['triggers'])[0], thresholds = zip(*pars['lepton']['triggers'])[1]),
            supy.calculables.other.Ratio("nVertex", binning = (15,-0.5,14.5), thisSample = pars['baseSample'],
                                         target = ("SingleMu",[]), groups = [('qcd_mg',[]),('qcd_py6',[]),('w_jets_fj_mg',[]),
                                                                        ('tt_tauola_fj',['tt_tauola_fj%s.tw.nvr'%s for s in ['','.wNonQQbar','.wTopAsymP00']])]),
            ] + self.xcleanSteps(pars) + [
            supy.steps.histos.value("%sTriggeringPt%s"%lepton, 200,0,200),
            supy.steps.filters.value("%sTriggeringPt%s"%lepton, min = lPtMin),
            supy.steps.histos.value(obj["sumPt"],50,0,1500),
            supy.steps.histos.value("rho",100,0,40),
            ] + self.selectionSteps(pars, withPlots = True) + [
            #supy.steps.filters.label('before top reco').invert(),#####################################
            supy.steps.filters.multiplicity("TopReconstruction",min=1),
            supy.steps.filters.label("selection complete"),
            supy.steps.histos.value("%sM3%s"%obj['jet'], 20,0,800),
            supy.steps.histos.value("KarlsruheDiscriminant", 28, -320, 800 ),
            supy.steps.histos.value("TopRatherThanWProbability",100,0,1),
            supy.steps.histos.value("fitTopRadiativeCoherence", 100,-1,1),
            #supy.calculables.other.Discriminant( fixes = ("","TopQqQg"),
            #                                left = {"pre":"qq", "tag":"top_muon_pf", "samples":['tt_tauola_fj.wNonQQbar.tw.nvr']},
            #                                right = {"pre":"qg", "tag":"top_muon_pf", "samples":['tt_tauola_fj.wTopAsymP00.tw.nvr']},
            #                                dists = {"fitTopPtOverSumPt" : (20,0,1),
            #                                         "fitTopCosThetaDaggerTT" : (40,-1,1),
            #                                         "fitTopSumP4AbsEta" : (21,0,7),
            #                                         "%sIndices%s.size"%obj["jet"] : (10,-0.5,9.5)
            #                                         },
            #                                correlations = True,
            #                                bins = 14),
            #supy.steps.filters.label('before discriminants').invert(),#####################################
            supy.calculables.other.Discriminant( fixes = ("","TopW"),
                                                 left = {"pre":"w_jets_fj_mg", "tag":"top_muon_pf", "samples":[]},
                                                 right = {"pre":"tt_tauola_fj", "tag":"top_muon_pf", "samples": ['tt_tauola_fj.%s.tw.nvr'%s for s in ['wNonQQbar','wTopAsymP00']]},
                                                 correlations = True,
                                                 dists = {"%sKt%s"%obj["jet"] : (25,0,150),
                                                          "%sB0pt%s"%obj["jet"] : (30,0,300),
                                                          "%s3absEta%s"%obj["jet"] : (20,0,4),
                                                          "fitTopHadChi2"     : (20,0,100),
                                                          "mixedSumP4.pt"     : (30,0,180),
                                                          #"fitTopLeptonPt"    : (30,0,180),  # not so powerful?
                                                          "fitTopDeltaPhiLNu" : (20,0,math.pi),
                                                          "TopRatherThanWProbability" : (20,0,1),
                                                          }),
            supy.calculables.other.Discriminant( fixes = ("","TopQCD"),
                                                 left = {"pre":"SingleMu", "tag":"QCD_muon_pf", "samples":[]},
                                                 right = {"pre":"tt_tauola_fj", "tag":"top_muon_pf", "samples": ['tt_tauola_fj.%s.tw.nvr'%s for s in ['wNonQQbar','wTopAsymP00']]},
                                                 correlations = True,
                                                 dists = {"%sKt%s"%obj["jet"] : (25,0,150),
                                                          "%sB0pt%s"%obj["jet"] : (30,0,300),
                                                          "%s3absEta%s"%obj["jet"] : (20,0,4),
                                                          "%sMt%s"%obj['muon']+"mixedSumP4" : (30,0,180),
                                                          "%sDeltaPhiB01%s"%obj["jet"] : (20,0,math.pi),
                                                          #"mixedSumP4.pt"     : (30,0,180),
                                                          #"fitTopLeptonPt"    : (30,0,180),
                                                          #"fitTopDeltaPhiLNu" : (20,0,math.pi),
                                                          }),
            supy.calculables.other.Discriminant( fixes = ("","WQCD"),
                                                 left = {"pre":"w_jets_fj_mg", "tag":"top_muon_pf", "samples":[]},
                                                 right = {"pre":"SingleMu", "tag":"QCD_muon_pf", "samples":[]},
                                                 correlations = True,
                                                 dists = {"%sB0pt%s"%obj["jet"] : (30,0,300),
                                                          "%sMt%s"%obj['muon']+"mixedSumP4" : (30,0,180),
                                                          "%sDeltaPhiB01%s"%obj["jet"] : (20,0,math.pi),
                                                          "fitTopCosHelicityThetaL": (20,-1,1),
                                                          }),
            calculables.gen.qDirProbPlus('fitTopSumP4Eta', 10, 'top_muon_pf', 'tt_tauola_fj.wTopAsymP00.tw.nvr', path = self.globalStem),
            #supy.steps.filters.label('before signal distributions').invert(),#####################################
            supy.steps.histos.multiplicity("%sIndices%s"%obj["jet"]),
            supy.steps.histos.value("TriDiscriminant",50,-1,1),
            steps.top.Asymmetry(('fitTop',''), bins = 640),
            steps.top.Spin(('fitTop','')),

            #steps.histos.value('fitTopSumP4Eta', 12, -6, 6),
            #steps.filters.absEta('fitTopSumP4', min = 1),
            #steps.histos.value('fitTopSumP4Eta', 12, -6, 6),
            #steps.top.Asymmetry(('fitTop',''), bins = 640),
            #steps.top.Spin(('fitTop','')),

            #steps.top.kinFitLook("fitTopRecoIndex"),
            #steps.filters.value("TriDiscriminant",min=-0.64,max=0.8),
            #steps.histos.value("TriDiscriminant",50,-1,1),
            #steps.top.Asymmetry(('fitTop',''), bins = 640),
            #steps.top.Spin(('fitTop','')),
            #steps.filters.value("TriDiscriminant",min=-.56,max=0.72),
            #steps.histos.value("TriDiscriminant",50,-1,1),
            #steps.top.Asymmetry(('fitTop','')),
            #steps.top.Spin(('fitTop','')),
            ])
    ########################################################################################


    ########################################################################################
    def concludeAll(self) :
        self.rowcolors = [r.kBlack, r.kGray+3, r.kGray+2, r.kGray+1, r.kViolet+4]
        super(topAsymm,self).concludeAll()
        #self.meldWpartitions()
        #self.meldQCDpartitions()
        self.meldScale()
        #self.dilutions()
        #self.measureQQbarComponent()
        self.plotMeldScale()
        #self.ensembleTest()
        #self.PEcurves()

    def conclude(self,pars) :
        org = self.organizer(pars)
        org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
        org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
        org.mergeSamples(targetSpec = {"name":"t#bar{t}", "color":r.kViolet}, sources=["tt_tauola_fj.wNonQQbar.tw.nvr","tt_tauola_fj.wTopAsymP00.tw.nvr"], keepSources = True)
        org.mergeSamples(targetSpec = {"name":"t#bar{t}.q#bar{q}.N30", "color":r.kRed}, sources = ["tt_tauola_fj.wTopAsymN30.tw.nvr","tt_tauola_fj.wNonQQbar.tw.nvr"][:1])
        org.mergeSamples(targetSpec = {"name":"t#bar{t}.q#bar{q}.P30", "color":r.kGreen}, sources = ["tt_tauola_fj.wTopAsymP30.tw.nvr","tt_tauola_fj.wNonQQbar.tw.nvr"][:1])
        org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+2}, sources = ["qcd_py6","t#bar{t}","w_jets_fj_mg.tw.nvr"], keepSources = True)
        #for ss in filter(lambda ss: 'tt_tauola' in ss['name'],org.samples) : org.drop(ss['name'])

        orgpdf = copy.deepcopy(org)
        orgpdf.scale( toPdf = True )
        org.scale( lumiToUseInAbsenceOfData = 1.1e3 )

        names = [ss["name"] for ss in org.samples]
        kwargs = {"detailedCalculables": False,
                  "blackList":["lumiHisto","xsHisto","nJobsHisto"],
                  "samplesForRatios" : next(iter(filter(lambda x: x[0] in names and x[1] in names, [("Data 2011","standard_model")])), ("","")),
                  "sampleLabelsForRatios" : ("data","s.m."),
                  "detailedCalculables" : True,
                  "rowColors" : self.rowcolors,
                  }
        
        plotter.plotter(org, psFileName = self.psFileName(org.tag+"_log"),  doLog = True, pegMinimum = 0.01, **kwargs ).plotAll()
        plotter.plotter(org, psFileName = self.psFileName(org.tag+"_nolog"), doLog = False, **kwargs ).plotAll()

        kwargs["samplesForRatios"] = ("","")
        kwargs["dependence2D"] = True
        plotter.plotter(orgpdf, psFileName = self.psFileName(org.tag+"_pdf"), doLog = False, **kwargs ).plotAll()

    def meldWpartitions(self) :
        samples = {"top_muon_pf" : ["w_"],
                   "Wlv_muon_pf" : ["w_","SingleMu"],
                   "QCD_muon_pf" : []}
        organizers = [organizer.organizer(tag, [s for s in self.sampleSpecs(tag) if any(item in s['name'] for item in samples[tag])])
                      for tag in [p['tag'] for p in self.readyConfs]]
        if len(organizers)<2 : return
        for org in organizers :
            org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
            org.mergeSamples(targetSpec = {"name":"w_mg", "color":r.kRed if "Wlv" in org.tag else r.kBlue, "markerStyle": 22}, sources = ["w_jets_fj_mg.tw.nvr"])
            org.scale(toPdf=True)

        melded = organizer.organizer.meld("wpartitions",filter(lambda o: o.samples, organizers))
        pl = plotter.plotter(melded,
                             psFileName = self.psFileName(melded.tag),
                             doLog = False,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             rowColors = self.rowcolors,
                             ).plotAll()

    def meldQCDpartitions(self) :
        samples = {"top_muon_pf" : ["qcd_py6fjmu"],
                   "Wlv_muon_pf" : [],
                   "QCD_muon_pf" : ["qcd_py6fjmu","SingleMu"]}
        organizers = [organizer.organizer(tag, [s for s in self.sampleSpecs(tag) if any(item in s['name'] for item in samples[tag])])
                      for tag in [p['tag'] for p in self.readyConfs]]
        if len(organizers)<2 : return
        for org in organizers :
            org.mergeSamples(targetSpec = {"name":"Data 2011", "color":r.kBlack, "markerStyle":20}, allWithPrefix="SingleMu")
            org.mergeSamples(targetSpec = {"name":"qcd_py6mu", "color":r.kRed if "QCD" in org.tag else r.kBlue, "markerStyle": 22}, allWithPrefix="qcd_py6fjmu")
            org.scale(toPdf=True)

        melded = organizer.organizer.meld("qcdPartitions",filter(lambda o: o.samples, organizers))
        pl = plotter.plotter(melded,
                             psFileName = self.psFileName(melded.tag),
                             doLog = False,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             rowColors = self.rowcolors,
                             ).plotAll()

    def plotMeldScale(self) :
        if not hasattr(self,"orgMelded") : print "run meldScale() before plotMeldScale()"; return
        melded = copy.deepcopy(self.orgMelded)
        for ss in filter(lambda ss: 'tt_tauola_fj' in ss['name'], melded.samples) : melded.drop(ss['name'])
        pl = plotter.plotter(melded, psFileName = self.psFileName(melded.tag),
                             doLog = False,
                             blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                             rowColors = self.rowcolors,
                             samplesForRatios = ("top.Data 2011","S.M."),
                             sampleLabelsForRatios = ('data','s.m.')
                             ).plotAll()

    def meldScale(self) :
        meldSamples = {"top_muon_pf" : ["SingleMu","tt_tauola_fj","w_jets"],
                       #"Wlv_muon_pf" : ["w_jets"],
                       "QCD_muon_pf" : ["SingleMu"]}
        
        organizers = [organizer.organizer(tag, [s for s in self.sampleSpecs(tag) if any(item in s['name'] for item in meldSamples[tag])])
                      for tag in [p['tag'] for p in self.readyConfs if p["tag"] in meldSamples]]
        if len(organizers) < len(meldSamples) : return
        for org in organizers :
            org.mergeSamples(targetSpec = {"name":"t#bar{t}", "color":r.kViolet}, sources=["tt_tauola_fj.wNonQQbar.tw.nvr","tt_tauola_fj.wTopAsymP00.tw.nvr"], keepSources = True)
            org.mergeSamples(targetSpec = {"name":"w_jets", "color":r.kRed}, allWithPrefix = "w_jets")
            org.mergeSamples(targetSpec = {"name":"Data 2011",
                                           "color":r.kBlue if "QCD_" in org.tag else r.kBlack,
                                           "markerStyle":(20 if "top" in org.tag else 1)}, allWithPrefix="SingleMu")

        self.orgMelded = organizer.organizer.meld(organizers = organizers)

        def measureFractions(dist) :
            before = next(self.orgMelded.indicesOfStep("label","selection complete"))
            distTup = self.orgMelded.steps[next(iter(filter(lambda i: before<i, self.orgMelded.indicesOfStepsWithKey(dist))))][dist]
            #distTup = self.orgMelded.steps[next(self.orgMelded.indicesOfStepsWithKey(dist))][dist]

            templateSamples = ['top.t#bar{t}','top.w_jets','QCD.Data 2011']
            templates = [None] * len(templateSamples)
            for ss,hist in zip(self.orgMelded.samples,distTup) :
                contents = [hist.GetBinContent(i) for i in range(hist.GetNbinsX()+2)]
                if ss['name'] == "top.Data 2011" :
                    observed = contents
                    nEventsObserved = sum(observed)
                elif ss['name'] in templateSamples :
                    templates[templateSamples.index(ss['name'])] = contents
                else : pass
        
            from core.fractions import componentSolver,drawComponentSolver
            cs = componentSolver(observed, templates, 1e4)
            csCanvas = drawComponentSolver(cs)
            name = "measuredFractions_%s"%dist
            utils.tCanvasPrintPdf(csCanvas[0], "%s/%s"%(self.globalStem,name))
            with open(self.globalStem+"/%s.txt"%name,"w") as file :
                print >> file, cs
                print >> file, cs.components
            return distTup,cs

        distTup,cs = map(measureFractions,["KarlsruheDiscriminant","TriDiscriminant"])[-1]

        fractions = dict(zip(templateSamples,cs.fractions))        
        for iSample,ss in enumerate(self.orgMelded.samples) :
            if ss['name'] in fractions : self.orgMelded.scaleOneRaw(iSample, fractions[ss['name']] * nEventsObserved / distTup[iSample].Integral(0,distTup[iSample].GetNbinsX()+1))
        self.orgMelded.mergeSamples(targetSpec = {"name":"S.M.", "color":r.kGreen+2}, sources = ['top.w_jets','top.t#bar{t}','QCD.Data 2011'], keepSources = True, force = True)

    def dilutions(self) :
        import itertools
        fileName = '%s/dilutions.txt'%self.globalStem
        with open(fileName, "w") as file :
            names = [ss['name'] for ss in self.orgMelded.samples]
            iSamples = [names.index(n) for n in ['top.t#bar{t}','top.w_jets','QCD.Data 2011','top.tt_tauola_fj.wNonQQbar.tw.nvr','top.tt_tauola_fj.wTopAsymP00.tw.nvr']]
            for i,iS in enumerate(iSamples) : print >> file, i,names[iS]
            print >> file
            print >> file, ''.rjust(40), ''.join(("[%d,%d]"%pair).rjust(10) for pair in itertools.combinations(range(len(iSamples)), 2))
            for step in self.orgMelded.steps :
                if not any("Discriminant" in item for item in step.nameTitle) : continue
                print >> file
                print >> file
                print >> file, utils.hyphens
                print >> file, step.name, step.title
                print >> file, utils.hyphens
                print >> file
                for hname,hists in step.iteritems() :
                    if issubclass(type(next(iter(filter(None,hists)))),r.TH2) : continue
                    aHists = [[hists[i].GetBinContent(j) for j in range(0,hists[i].GetNbinsX()+2)] for i in iSamples]
                    print >> file, hname.rjust(40), ''.join([(("%.3f"%round(utils.dilution(A,B),3))).rjust(10) for A,B in itertools.combinations(aHists,2)])
        print "Output file: %s"%fileName

    def PEcurves(self) :
        if not hasattr(self, 'orgMelded') : return
        specs = ([{'var' : "ak5JetPFNTrkHiEffPat[i[%d]]:xcak5JetPFIndicesBtaggedPat"%bIndex, 'left':True, 'right':False} for bIndex in [0,1,2]] +
                 [{'var' : "TopRatherThanWProbability",                                      'left':True, 'right':False},
                  {'var' : "TriDiscriminant",                                                'left':True, 'right':True}])
        pes = {}
        for spec in specs :
            dists = dict(zip([ss['name'] for ss in self.orgMelded.samples ],
                             self.orgMelded.steps[next(self.orgMelded.indicesOfStepsWithKey(spec['var']))][spec['var']] ) )
            contours = utils.optimizationContours( [dists['top.t#bar{t}']],
                                                   [dists[s] for s in ['QCD.Data 2011','top.w_jets']],
                                                   **spec
                                                   )
            utils.tCanvasPrintPdf(contours[0], "%s/PE_%s"%(self.globalStem,spec['var']))
            if spec['left']^spec['right'] : pes[spec['var']] = contours[1]
        c = r.TCanvas()
        leg = r.TLegend(0.5,0.8,1.0,1.0)
        graphs = []
        for i,(var,pe) in enumerate(pes.iteritems()) :
            pur,eff = zip(*pe)
            g = r.TGraph(len(pe), np.array(eff), np.array(pur))
            g.SetTitle(";efficiency;purity")
            g.SetLineColor(i+2)
            leg.AddEntry(g,var,'l')
            graphs.append(g)
            g.Draw('' if i else 'AL')
        leg.Draw()
        c.Update()
        utils.tCanvasPrintPdf(c, "%s/purity_v_efficiency"%self.globalStem)
        return

    def measureQQbarComponent(self) :
        dist = "DiscriminantTopQqQg"
        dists = dict(zip([ss['name'] for ss in self.orgMelded.samples ],
                         self.orgMelded.steps[next(self.orgMelded.indicesOfStepsWithKey(dist))][dist] ) )
        def contents(name) : return np.array([dists[name].GetBinContent(i) for i in range(dists[name].GetNbinsX()+2)])

        from core.fractions import componentSolver, drawComponentSolver
        cs = componentSolver(observed = contents('top.Data 2011'),
                             components = [ contents('top.tt_tauola_fj.wTopAsymP00.tw.nvr'), contents('top.tt_tauola_fj.wNonQQbar.tw.nvr')],
                             ensembleSize = 1e4,
                             base = contents('top.w_jets') + contents('QCD.Data 2011')
                             )
        csCanvas = drawComponentSolver(cs)
        utils.tCanvasPrintPdf(csCanvas[0], "%s/measuredQQFractions"%self.globalStem)
        with open(self.globalStem+"/measuredQQFractions.txt","w") as file :  print >> file, cs


    def templates(self, iStep, dist, qqFrac) :
        if not hasattr(self,'orgMelded') : print 'run meldScale() before asking for templates()'; return
        topQQs = [s['name'] for s in self.orgMelded.samples if 'wTopAsym' in s['name']]
        asymm = [eval(name.replace("top.tt_tauola_fj.wTopAsym","").replace(".tw.nvr","").replace("P",".").replace("N","-.")) for name in topQQs]
        distTup = self.orgMelded.steps[iStep][dist]
        edges = utils.edgesRebinned( distTup[ self.orgMelded.indexOfSampleWithName("S.M.") ], targetUncRel = 0.015, offset = 2 )

        def nparray(name, scaleToN = None) :
            hist_orig = distTup[ self.orgMelded.indexOfSampleWithName(name) ]
            hist = hist_orig.Rebin(len(edges)-1, "%s_rebinned"%hist_orig.GetName(), edges)
            bins = np.array([hist.GetBinContent(j) for j in range(hist.GetNbinsX()+2)])
            if scaleToN : bins *= (scaleToN / sum(bins))
            return bins

        nTT = sum(nparray('top.t#bar{t}'))
        observed = nparray('top.Data 2011')
        base = ( nparray('QCD.Data 2011') +
                 nparray('top.w_jets') +
                 nparray('top.tt_tauola_fj.wNonQQbar.tw.nvr', scaleToN = (1-qqFrac) * nTT )
                 )
        templates = [base +  nparray(qqtt, qqFrac*nTT ) for qqtt in topQQs]
        return zip(asymm, templates), observed
    

    def ensembleFileName(self, iStep, dist, qqFrac, suffix = '.pickleData') :
        return "%s/ensembles/%d_%s_%.3f%s"%(self.globalStem,iStep,dist,qqFrac,suffix)

    def ensembleTest(self) :
        qqFracs = sorted([0.10, 0.12, 0.15, 0.20, 0.25, 0.30, 0.40, 0.60, 1.0])
        dists = ['lHadtDeltaY',
                 'ttbarDeltaAbsY',
                 'leptonRelativeY',
                 'ttbarSignedDeltaY'
                ]
        args = sum([[(iStep, dist, qqFrac) for iStep in list(self.orgMelded.indicesOfStepsWithKey(dist))[:None] for qqFrac in qqFracs] for dist in dists],[])
        utils.operateOnListUsingQueue(6, utils.qWorker(self.pickleEnsemble), args)
        ensembles = dict([(arg,utils.readPickle(self.ensembleFileName(*arg))) for arg in args])

        for iStep in sorted(set([iStep for iStep,dist,qqFrac in ensembles])) :
            canvas = r.TCanvas()
            dists = sorted(set([dist for jStep,dist,qqFrac in ensembles if jStep==iStep]))
            legend = r.TLegend(0.7,0.5,0.9,0.9)
            graphs = {}
            for iDist,dist in enumerate(dists) :
                points = sorted([(qqFrac,ensemble.sensitivity) for (jStep, jDist, qqFrac),ensemble in ensembles.iteritems() if jStep==iStep and jDist==dist])
                qqs,sens = zip(*points)
                graphs[dist] = r.TGraph(len(points),np.array(qqs),np.array(sens))
                graphs[dist].SetLineColor(iDist+1)
                graphs[dist].Draw('' if iDist else "AL")
                graphs[dist].SetMinimum(0)
                graphs[dist].SetTitle("Sensitivity @ step %d;fraction of t#bar{t} from q#bar{q};expected uncertainty on R"%iStep)
                legend.AddEntry(graphs[dist],dist,'l')
            legend.Draw()
            utils.tCanvasPrintPdf(canvas, '%s/sensitivity_%d'%(self.globalStem,iStep))
                
    def pickleEnsemble(self, iStep, dist, qqFrac ) :
        utils.mkdir(self.globalStem+'/ensembles')
        templates,observed = self.templates(iStep, dist, qqFrac)
        ensemble = supy.utils.templateFit.templateEnsembles(2e3, *zip(*templates) )
        utils.writePickle(self.ensembleFileName(iStep,dist,qqFrac), ensemble)

        name = self.ensembleFileName(iStep,dist,qqFrac,'')
        canvas = r.TCanvas()
        canvas.Print(name+'.ps[')
        stuff = supy.utils.templateFit.drawTemplateEnsembles(ensemble, canvas)
        canvas.Print(name+".ps")
        import random
        for i in range(20) :
            par, templ = random.choice(zip(ensemble.pars,ensemble.templates)[2:-2])
            pseudo = [np.random.poisson(mu) for mu in templ]
            tf = supy.utils.templateFit.templateFitter(pseudo,ensemble.pars,ensemble.templates, 1e3)
            stuff = supy.utils.templateFit.drawTemplateFitter(tf,canvas, trueVal = par)
            canvas.Print(name+".ps")
            for item in sum([i if type(i) is list else [i] for i in stuff[1:]],[]) : utils.delete(item)

        canvas.Print(name+'.ps]')
        os.system('ps2pdf %s.ps %s.pdf'%(name,name))
        os.system('rm %s.ps'%name)
        
    def templateFit(self, iStep, dist, qqFrac = 0.15) :
        print "FIXME"; return
        if not hasattr(self,'orgMelded') : print 'run meldScale() before templateFit().'; return

        outName = self.globalStem + '/templateFit_%s_%d'%(dist,qqFrac*100)
        #TF = templateFit.templateFitter(observed, *zip(*templates) )
        #print utils.roundString(TF.value, TF.error , noSci=True)
        
        #stuff = templateFit.drawTemplateFitter(TF, canvas)
        #canvas.Print(outName+'.ps')
        #for item in sum([i if type(i) is list else [i] for i in stuff[1:]],[]) : utils.delete(item)
        
        #canvas.Print(outName+'.ps]')
        #os.system('ps2pdf %s.ps %s.pdf'%(outName,outName))
        #os.system('rm %s.ps'%outName)
