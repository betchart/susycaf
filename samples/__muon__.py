import samples
from sites import srm
muon = samples.SampleHolder()

muon.add("SingleMu.2011A-May.1",'%s/bbetchar/ICF/automated/2011_11_06_08_14_36/")'%srm, lumi = 200.1519)
muon.add("SingleMu.2011A-PR4.1",'%s/bbetchar/ICF/automated/2011_11_06_08_25_27/",alwaysUseLastAttempt = True)'%srm, lumi = 886.7901)
muon.add("SingleMu.2011A-Aug.1",'%s/bbetchar/ICF/automated/2011_11_06_08_35_40/")'%srm, lumi = 356.7521)
muon.add("SingleMu.2011A-Oct.1",'%s/bbetchar/ICF/automated/2011_11_06_08_44_13/")'%srm, lumi = 641.7003)
muon.add("SingleMu.2011B-PR1.1a",'%s//bbetchar/ICF/automated/2011_11_06_20_02_03/",alwaysUseLastAttempt = True)'%srm, lumi = 1049.6221)
muon.add("SingleMu.2011B-PR1.1b",'%s//bbetchar/ICF/automated/2011_11_06_20_11_30/",alwaysUseLastAttempt = True)'%srm, lumi = 1527.7806)

#L1Fast 2011
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt",'%s/bbetchar/ICF/automated/2011_07_21_00_50_15/")'%srm, lumi = 887.2389)
muon.add("SingleMu.Run2011A-May10-v1.FJ.Burt",'%s/bbetchar/ICF/automated/2011_07_21_00_42_38/")'%srm, lumi = 200.2046)
#
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt5",'%s/bbetchar//ICF/automated/2011_07_07_11_29_08/")'%srm, lumi = 115.20 )
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt4",'%s/bbetchar//ICF/automated/2011_07_02_11_34_55/")'%srm, lumi = 94.43 )
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt3",'%s/bbetchar//ICF/automated/2011_06_24_18_49_40/",alwaysUseLastAttempt = True)'%srm, lumi = 166.73 )
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt2",'%s/bbetchar//ICF/automated/2011_06_18_17_11_12/")'%srm, lumi = 216.43 )
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt1",'%s/bbetchar/ICF/automated/2011_06_11_17_10_04/")'%srm, lumi = 294.45 )
muon.add("SingleMu.Run2011A-May10-v1.FJ.Burt_",'%s/bbetchar/ICF/automated/2011_06_11_17_16_01/")'%srm, lumi = 186.71 )
#skims, have pf muon |eta|<2.2, pt>24
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt_skim",    'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/SingleMu.Run2011A-PR-v4.FJ.Burt/SingleMu.Run2011A-PR-v4.FJ.Burt_*_skim.root", isDirectory = False)',   lumi = 2.944500e+02)
muon.add("SingleMu.Run2011A-May10-v1.FJ.Burt_skim", 'utils.fileListFromDisk(location = "/vols/cms02/bbetchar/01_skims/SingleMu.Run2011A-May10-v1.FJ.Burt/SingleMu.Run2011A-May10-v1.FJ.Burt_*_skim.root", isDirectory = False)',lumi = 1.865500e+02)

#2011
muon.add("SingleMu.Run2011A-PR-v2.Robin1",'%s/rnandi/ICF/automated/2011_05_02_11_24_48/")'%srm, lumi = 999999.9)
muon.add("SingleMu.Run2011A-PR-v2.Robin2",'%s/rnandi/ICF/automated/2011_05_07_17_01_57/")'%srm, lumi = 999999.9)
muon.add("SingleMu.Run2011A-PR-v2.Alex",'%s/as1604/ICF/automated/2011_04_25_17_30_19/")'%srm, lumi = 999999.9)
muon.add("SingleMu.Run2011A-PR-v2.Burt",'%s/bbetchar/ICF/automated/2011_05_18_22_24_58/")'%srm, lumi = 999999.9)

#skims requiring one tight muon with pT>23 GeV
dir = "/vols/cms02/elaird1/29_skims/05_muons/1mu"
muon.add("SingleMu.Run2011A-PR-v2.Alex_1muskim",   'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v2.Alex.jsonWeight_*_skim.root", isDirectory = False)'%dir,
         lumi = 1.227000e+01)
muon.add("SingleMu.Run2011A-PR-v2.Robin1_1muskim", 'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v2.Robin1.jsonWeight_*_skim.root", isDirectory = False)'%dir,
         lumi = 8.731000e+01)
muon.add("SingleMu.Run2011A-PR-v2.Robin2_1muskim", 'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v2.Robin2.jsonWeight_*_skim.root", isDirectory = False)'%dir,
         lumi = 7.934000e+01)
muon.add("tt_tauola_mg_1muskim", 'utils.fileListFromDisk(location = "%s/tt_tauola_mg_*_skim.root", isDirectory = False)'%dir, xs = 1.527872e-01 * 1.575000e+02)
muon.add("w_jets_mg_1muskim", 'utils.fileListFromDisk(location = "%s/w_jets_mg_*_skim.root", isDirectory = False)'%dir, xs = 1.774398e-01 * 3.192400e+04)
muon.add("dyll_jets_mg_1muskim", 'utils.fileListFromDisk(location = "%s/dyll_jets_mg_*_skim.root", isDirectory = False)'%dir,xs = 2.536323e-01 * 3.048000e+03)

##skims of the above requiring the leading muon with pT>25 GeV and a second muon with pT>10 GeV, and not a third muon with pT>10 GeV and ID
#dir = "/vols/cms02/elaird1/29_skims/05_muons/2mu"
#muon.add("SingleMu.Run2011A-PR-v2.Alex_2muskim",   'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v2.Alex_1muskim.jsonWeight_*_skim.root", isDirectory = False)'%dir, lumi = 1.227000e+01)
#muon.add("SingleMu.Run2011A-PR-v2.Robin1_2muskim", 'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v2.Robin1_1muskim.jsonWeight_*_skim.root", isDirectory = False)'%dir, lumi = 8.731000e+01)
#muon.add("SingleMu.Run2011A-PR-v2.Robin2_2muskim", 'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v2.Robin2_1muskim.jsonWeight_*_skim.root", isDirectory = False)'%dir, lumi = 7.934000e+01)
#muon.add("tt_tauola_mg_2muskim", 'utils.fileListFromDisk(location = "%s/tt_tauola_mg_1muskim_*_skim.root", isDirectory = False)'%dir, xs = 6.188606e-02 * 2.406398e+01)
#muon.add("w_jets_mg_2muskim", 'utils.fileListFromDisk(location = "%s/w_jets_mg_1muskim_*_skim.root", isDirectory = False)'%dir, xs = 2.163140e-05 * 5.664588e+03)
#muon.add("dyll_jets_mg_2muskim", 'utils.fileListFromDisk(location = "%s/dyll_jets_mg_1muskim_*_skim.root", isDirectory = False)'%dir, xs = 5.612258e-01 * 7.730713e+02)
#
#muon.add("325_scaled_data", 'utils.fileListFromDisk(location = "/home/hep/elaird1/85_muonLook/07_displays/325_scaled_data.root", isDirectory = False)', lumi = 1.0)

#skims requiring the leading muon with pT>32 GeV and a second muon with pT>10 GeV, and not a third muon with pT>10 GeV and ID
dir = "/vols/cms02/elaird1/29_skims/05_muons/2mu_v2"
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt2_2mu_skim",   'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v4.FJ.Burt2.jsonWeight_*_skim.root", isDirectory = False)'%dir,  lumi = 2.164300e+02)
muon.add("SingleMu.Run2011A-PR-v4.FJ.Burt_2mu_skim",    'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-PR-v4.FJ.Burt.jsonWeight_*_skim.root", isDirectory = False)'%dir,   lumi = 2.944500e+02)
muon.add("SingleMu.Run2011A-May10-v1.FJ.Burt_2mu_skim", 'utils.fileListFromDisk(location = "%s/SingleMu.Run2011A-May10-v1.FJ.Burt.jsonWeight_*_skim.root", isDirectory = False)'%dir,lumi = 1.865500e+02)
muon.add("tt_tauola_mg_2mu_skim", 'utils.fileListFromDisk(location = "%s/tt_tauola_mg_1muskim_*_skim.root", isDirectory = False)'%dir,xs = 5.538402e-02 * 2.406398e+01)
muon.add("dyll_jets_mg_2mu_skim", 'utils.fileListFromDisk(location = "%s/dyll_jets_mg_1muskim_*_skim.root", isDirectory = False)'%dir,xs = 4.605050e-01 * 7.730713e+02)
muon.add("w_jets_mg_2mu_skim",    'utils.fileListFromDisk(location = "%s/w_jets_mg_1muskim_*_skim.root", isDirectory = False)'%dir,   xs = 1.454525e-05 * 5.664588e+03)
        
