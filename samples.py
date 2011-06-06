import collections, configuration

def specify(names = [], overrideLumi = None, xsPostWeights = None, effectiveLumi = None, nFilesMax = None, nEventsMax = None, weights = [], color = 1, markerStyle = 1 ) :
    assert not (overrideLumi and type(names)==list)
    if type(names) != list : names = [names]
    if type(weights) != list : weights = [weights]
    samplespec = collections.namedtuple("samplespec", "name overrideLumi xsPostWeights effectiveLumi nFilesMax nEventsMax weights color markerStyle")
    return [samplespec(name,overrideLumi,xsPostWeights,effectiveLumi,nFilesMax,nEventsMax,weights,color,markerStyle) for name in names]
    
class SampleHolder(dict) :
    sample = collections.namedtuple("sample", "filesCommand xs lumi ptHatMin")
    overlapping = collections.namedtuple("overlappingSample", "samples")

    def __init__(self) :
        self.overlappingSamples = []
    
    def update(self, other) :

        assert type(other) is type(self), "%s is not a SampleHolder" % str(type(other))
        for key in other : assert key not in self, "%s already specified" % key

        dict.update(self,other)
        map(lambda t: self.adjustOverlappingSamples(*t), other.overlappingSamples)

    def add(self, name, filesCommand = None, xs = None, lumi = None, ptHatMin = None) :

        assert lumi or xs,                      "Underspecified sample: %s"%name
        assert not (lumi and (xs or ptHatMin)), "Overspecified sample: %s"%name

        self[name] = self.sample(filesCommand, xs, lumi, ptHatMin)

    def adjustOverlappingSamples( self, listOfSamples) :
        assert len(listOfSamples) == len(set(listOfSamples)), "Duplicate samples in: %s"%str(listOfSamples)

        for s in listOfSamples :
            assert s in self, "Unknown sample"%s
            assert self[s].ptHatMin, "ptHatMin unspecified for sample: %s"%s
            for otherOverlappingSamples in self.overlappingSamples :
                assert s not in otherOverlappingSamples[0], "Sample in another unbinned group: %s"%s

        self.overlappingSamples.append( self.overlapping(listOfSamples) )

for module in configuration.samplesFiles() :
    exec("from samples%s import *"%module)
