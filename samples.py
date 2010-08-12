import collections

def specify(name = None, nFilesMax = -1, nEventsMax = -1, color = r.kBlack, markerStyle = 20 ) :
    samplespec = collections.namedtuple("samplespec", "name nFilesMax nEventsMax color markerStyle")
    return samplespec(name,nFilesMax,nEventsMax,color,markerStyle)
    
class SampleHolder(dict) :
    sample = collections.namedtuple("sample", "filesCommand xs lumi ptHatMin")
    overlapping = collections.namedtuple("overlappingSample", "samples useRejectionMethod")

    def __init__(self) :
        self.overlappingSamples = []
    
    def update(other) :

        assert type(other) is type(self), "%s is not a SampleHolder" % str(type(other))
        for key in other : assert key not in self, "%s already specified" % key

        self.update(other)
        map(lambda t: self.adjustOverlappingSamples(*t), other.overlappingSamples)

    def add(self, name, filesCommand = None, xs = None, lumi = None, ptHatMin = None) :

        assert lumi is None or xs is None,   "Underspecified sample: %s"%name
        assert lumi ^ (xs or ptHatMin), "Overspecified sample: %s"%name

        self[name] = self.sample(filesCommand, xs, lumi, ptHatMin)

    def adjustOverlappingSamples( self, listOfSamples, useRejectionMethod = True ) :
        assert len(listOfSamples) == len(set(listOfSamples)), "Duplicate samples in: %s"%str(listOfSamples)

        for s in listOfSamples :
            assert s in self, "Unknown sample"%s
            assert self[s].ptHatMin, "ptHatMin unspecified for sample: %s"%s
            for otherOverlappingSamples in self.overlappingSamples :
                assert s not in otherOverlappingSamples[0], "Sample in another unbinned group: %s"%s

        self.overlappingSamples.append( overlapping(listOfSamples, useRejectionMethod ) )

from samplesMC import *
