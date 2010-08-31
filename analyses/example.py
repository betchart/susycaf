#!/usr/bin/env python

import os
import analysis,utils,calculables,steps,samples,organizer,plotter
import ROOT as r

class example(analysis.analysis) :
    def baseOutputDirectory(self) :
        return "/tmp/%s/"%os.environ["USER"]

    def listOfSteps(self,params) :
        jets=("ak5JetPF","Pat")
        minJetPt=10.0
    
        outList=[
            steps.progressPrinter(),
            steps.techBitFilter([0],True),
            steps.physicsDeclared(),
            steps.vertexRequirementFilter(),
            steps.monsterEventFilter(),
            
            steps.jetPtSelector(jets,minJetPt,0),#leading corrected jet
            steps.jetPtSelector(jets,minJetPt,1),#next corrected jet
            #steps.jetPtVetoer( jets,minJetPt,2),#next corrected jet
            steps.multiplicityFilter("%sIndicesOther%s"%jets, nMax = 0),
            steps.multiplicityFilter("%sIndices%s"%jets, nMin = 2),
            
            steps.singleJetHistogrammer(jets,1), 
            steps.cleanJetHtMhtHistogrammer(jets),
            #steps.variableGreaterFilter(25.0,jets[0]+"SumPt"+jets[1]),
            
            steps.alphaHistogrammer(jets),
            #steps.skimmer("/tmp/%s/"%os.environ["USER"]),
            ]
        return outList
    
    def listOfCalculables(self,params) :
        jetTypes = [("ak5Jet","Pat"),("ak5JetJPT","Pat"),("ak5JetPF","Pat")]
        listOfCalculables = calculables.zeroArgs()
        listOfCalculables += calculables.fromCollections("calculablesJet",jetTypes)
        listOfCalculables += [ calculables.jetIndices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
        listOfCalculables += [ calculables.jetSumP4( collection = jetType, mcScaleFactor = 1.0) for jetType in jetTypes]
        listOfCalculables += [ calculables.deltaPhiStar( collection = jetType, ptMin = 0.0) for jetType in jetTypes]
        return listOfCalculables

    def listOfSampleDictionaries(self) :
        exampleDict = samples.SampleHolder()
        exampleDict.add("Example_Skimmed_900_GeV_Data", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_Data.root"]', lumi = 1.0e-5 ) #/pb
        exampleDict.add("Example_Skimmed_900_GeV_MC", '["/afs/cern.ch/user/e/elaird/public/susypvt/framework_take3/skimmed_900_GeV_MC.root"]',       xs = 1.0e3 ) #pb
        return [exampleDict]

    def listOfSamples(self,params) :
        return [samples.specify(name = "Example_Skimmed_900_GeV_Data", color = r.kBlack, markerStyle = 20),
                samples.specify(name = "Example_Skimmed_900_GeV_MC", color = r.kRed)
                ]

    def conclude(self) :
        #make a pdf file with plots from the histograms created above
        org = organizer.organizer( self.sampleSpecs() )
        org.scale()
        plotter.plotter( org,
                         psFileName = self.psFileName(),
                         samplesForRatios = ("Example_Skimmed_900_GeV_Data","Example_Skimmed_900_GeV_MC"),
                         sampleLabelsForRatios = ("data","sim"),
                         ).plotAll()
