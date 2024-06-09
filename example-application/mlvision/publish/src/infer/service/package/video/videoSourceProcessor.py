#
# videoSourceProcessor.py
#

from threading import Thread

from package import Config
from package.util import util
from . import VideoStream
from . import VideoSource

import time

class VideoSourceProcessor:
    def __init__(self, config, sourceType, source, name, framework):
        self.videoSources = []
        self.config = config
        self.videoSources.append(VideoSource(sourceType, source, name, framework))
        self.detector = None
       
    def addVideoSource(self, sourceType, source, name, framework):
        self.videoSources.append(VideoSource(sourceType, source, name, framework))

    def processThread(self, index, threaded):
        if threaded:
            Thread(target=self.process, args=(index,)).start()
        else:
            self.process(index)

    def process(self, index):
        videoSource = self.videoSources[index]
        videoStream = VideoStream(self.config, videoSource, index)
        videoStream.startThread()
        time.sleep(1)

        if self.config.getIsTFLite():
            from package.detect.tflite import TFLiteDetector
            from package.detect.tflite import TFLiteOpenCV

            videoSource.setDetector(TFLiteDetector(self.config))
            opencv = TFLiteOpenCV()
            self.config.setDetectorInitialized(True)

            print ("{:.7f} VideoSourceProcessor TFLite detection loop begins index ".format(time.time()), index, end="\n", flush=True)
            while True:
                detector = videoSource.getDetector()
                frame_current, frame_normalized, frame_faces, frame_gray = opencv.getFrame(self.config, videoStream, detector.getFloatingModel(), detector.getHeight(), detector.getWidth())
                inference_interval, boxes, classes, scores = detector.getInferResults(frame_normalized)
                self.update(self.config, self.videoSources, videoSource, detector.getLabels(), opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, inference_interval)

                # Any one thread may happen to check if reloadTFLite is True, then marks all videoSource to reload. Each thread will update the model looking at videoSource.reloadModel
                if self.config.getReloadTFLiteModel():
                    self.config.setReloadTFLiteModel(False)
                    for vSource in self.videoSources:
                        vSource.setReloadModel(True)

                if videoSource.getReloadModel():
                    videoSource.setReloadModel(False)
                    videoSource.setDetector(TFLiteDetector(self.config, "update"))
                
            videoStream.stop()


    def update(self, config, video_sources, video_source, labels, opencv, frame_current, frame_faces, frame_gray, boxes, classes, scores, inference_interval):
        entities_dict = opencv.annotateFrame(config, labels, frame_current, video_source.getName(), frame_faces, frame_gray, boxes, classes, scores)

        if config.shouldShowOverlay():
            opencv.addOverlay(frame_current, config.getTool(), config.getDeviceName(), inference_interval, opencv.getFrameRate())

        video_source.frame_annotated = frame_current.copy()

        inference_data_json = opencv.getInferenceDataJSON(config, inference_interval, entities_dict, video_sources)

        if config.shouldPublishStream():
            util.inference_publish(config.getPublishPayloadStreamUrl(), inference_data_json)

        opencv.updateFrameRate()
