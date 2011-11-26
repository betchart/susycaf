import supy,steps,calculables,samples,ROOT as r

class prescales2(supy.analysis) :
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
        return {"muon" : ("muon","PF"),
                "triggers": self.mutriggers()
                }
    
    def listOfCalculables(self,pars) :
        return (supy.calculables.zeroArgs(supy.calculables) +
                supy.calculables.zeroArgs(calculables) +
                supy.calculables.fromCollections(calculables.muon,[pars["muon"]]) +
                [calculables.muon.Indices( pars["muon"], ptMin = 10, combinedRelIsoMax = 0.15),
                 calculables.muon.IndicesTriggering(pars['muon'], ptMin = 10),
                 calculables.other.lowestUnPrescaledTrigger(zip(*pars["triggers"])[0]),
                 calculables.vertex.ID(),
                 calculables.vertex.Indices(),
                 ])

    def listOfSteps(self,pars) :
        return [
            supy.steps.printer.progressPrinter(),
            supy.steps.filters.multiplicity("vertexIndices",min=1),
            steps.trigger.l1Filter("L1Tech_BPTX_plus_AND_minus.v0"),
            steps.trigger.physicsDeclaredFilter(),
            steps.filters.monster(),
            steps.filters.hbheNoise(),
            supy.steps.filters.value("%sTriggeringPt%s"%pars["muon"],min=10),
            steps.trigger.prescaleLumiEpochs(pars['triggers']),
            steps.trigger.anyTrigger(zip(*pars['triggers'])[0], unreliable = self.unreliableTriggers()),
            supy.steps.histos.value("%sTriggeringPt%s"%pars["muon"],100,0,200),
            steps.trigger.hltPrescaleHistogrammer(zip(*pars["triggers"])[0]),
            steps.trigger.lowestUnPrescaledTriggerHistogrammer(),
            steps.trigger.lowestUnPrescaledTriggerFilter(),
            supy.steps.histos.value("%sTriggeringPt%s"%pars["muon"],100,0,200),
            ]+[ steps.trigger.prescaleScan(trig,ptMin,"%sTriggeringPt%s"%pars['muon']) for trig,ptMin in pars['triggers']]+[
            supy.steps.filters.value( "%sTriggeringPt%s"%pars['muon'],min = 41)]

    def listOfSampleDictionaries(self) : return [samples.muon]

    def listOfSamples(self,params) :
        return ( supy.samples.specify( names = "SingleMu.2011B-PR1.1b", color = r.kViolet) +
                 supy.samples.specify( names = "SingleMu.2011B-PR1.1a", color = r.kOrange) +
                 supy.samples.specify( names = "SingleMu.2011A-Oct.1", color = r.kBlack) +
                 supy.samples.specify( names = "SingleMu.2011A-Aug.1", color = r.kGreen) +
                 supy.samples.specify( names = "SingleMu.2011A-PR4.1", color = r.kRed) +
                 supy.samples.specify( names = "SingleMu.2011A-May.1", color = r.kBlue) )
    
    def conclude(self,pars) :
        import re
        org = self.organizer(pars)
        black = sum([[hist for hist in step if re.match(r"HLT_Mu\d*_v\d*_p\d*",hist)] for step in org.steps],[])

        
        args = {"blackList":["lumiHisto","xsHisto","nJobsHisto"] + black,
                "detailedCalculables" : True }

        supy.plotter(org, psFileName = self.psFileName(org.tag+"unmerged"), **args ).plotAll()
        supy.plotter(org, psFileName = self.psFileName(org.tag+"unmerged_nolog"), doLog=False, **args ).plotAll()
        org.mergeSamples(targetSpec = {"name":"SingleMu","color":r.kRed}, allWithPrefix="SingleMu")
        supy.plotter(org, psFileName = self.psFileName(org.tag), **args ).plotAll()
        self.printPrescales(org)

                
    def printPrescales(self,org) :
        with open('output.txt','w') as file :
            print >> file, "\t     ptMin\t    prescale  observed\t\tN pass"
            for step in org.steps :
                if step.name != "prescaleScan" : continue
                for hist in sorted(step,key = lambda h: int(h.replace("_eta2p1","-2.1").split("_")[3][1:])) :
                    if not step[hist][0].GetBinContent(2) : continue
                    label =''.join(part.strip('p').rjust(8) for part in hist.replace("_eta2p1","-2.1").split('_'))
                    listed = int(hist.replace("_eta2p1","-2.1").split("_")[3][1:])
                    observed = step[hist][0].GetEntries() / step[hist][0].GetBinContent(2)
                    print >> file, label, ("%.1f" % observed).ljust(10), ("%.1f"%(observed/listed)).rjust(7), ("%d"%step[hist][0].GetBinContent(2)).rjust(20)

