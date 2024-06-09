#
# videoSource.py
#

class VideoSource:
    def __init__(self, sourceType, source, name, framework):
        self.sourceType = sourceType
        self.source = source
        self.name = name
        self.framework = framework
        self.index = None
        self.resolution = None
        self.detector = None
        self.frame_annotated = None
        self.reloadModel = False
        
    def getSourceType(self):
        return self.sourceType

    def getSource(self):
        return self.source

    def getName(self):
        return self.name

    def getFramework(self):
        return self.framework

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def setResolution(self, resolution):
        self.resolution = resolution

    def getResolution(self):
        return self.resolution

    def getResolutionWidth(self):
        return self.resolution[0]

    def getResolutionHeight(self):
        return self.resolution[1]

    def setDetector(self, detector):
        self.detector = detector
 
    def getDetector(self):
        return self.detector

    def setReloadModel(self, flag):
        self.reloadModel = flag
 
    def getReloadModel(self):
        return self.reloadModel
 
    
