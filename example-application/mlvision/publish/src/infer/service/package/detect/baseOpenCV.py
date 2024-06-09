#
# baseOpenCV.py
#

import base64
import cv2
import datetime
import json
import math
import numpy 
import time

class BaseOpenCV:
    def __init__(self):
        self.frame_rate  = 1 # seed value. Will get updated
        self.tickFrequency = cv2.getTickFrequency()
        self.t1 = cv2.getTickCount()
        
    def getFrameRate(self):
        return self.frame_rate

    def updateFrameRate(self):
        t2 = cv2.getTickCount()
        time1 = (t2 - self.t1)/self.tickFrequency
        self.frame_rate = 1/time1
    
    def getFrame(self, config, videostream, isFloatingModel, height, width):
        self.t1 = cv2.getTickCount()
        frame_read = videostream.read()
        frame_current = frame_read.copy()
        frame_rgb = cv2.cvtColor(frame_current, cv2.COLOR_BGR2RGB)
        frame_resize = cv2.resize(frame_rgb, (width, height))

        frame_faces = None
        frame_gray = None

        # Condition and Normalize pixel values
        frame_norm = numpy.expand_dims(frame_resize, axis=0)
        if isFloatingModel:
            frame_norm = (numpy.float32(frame_norm) - config.getInputMean()) / config.getInputStd()

        return frame_current, frame_norm, frame_faces, frame_gray
    
    def addOverlay(self, frame_current, tool, device_name, inference_interval, frame_rate): 
        alpha = 0.6
        overlay = frame_current.copy()
        cv2.rectangle(overlay, (2, 30), (215, 125), (64, 64, 64), -1)
        cv2.addWeighted(overlay, alpha, frame_current, 1 - alpha, 0, frame_current)
        cv2.putText(frame_current, '{tool}'.format(tool=tool), (5, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame_current, '{device_name}'.format(device_name=device_name), (5, 80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame_current, 'Detection Time {0:.2f} sec'.format(inference_interval), (5, 100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame_current, 'Overall FPS {0:.2f}'.format(frame_rate), (5, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1, cv2.LINE_AA)
    
    def addStatus(self, config, frame_current, src_name):
        alpha = 0.7
        title = frame_current.copy()
        h, w = frame_current.shape[:2]
        cv2.rectangle(title, (0, 0), (w, 25), (64, 64, 64), -1)
        cv2.addWeighted(title, alpha, frame_current, 1 - alpha, 0, frame_current)
        cv2.putText(frame_current, src_name, (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame_current, 'GMT {0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), (w - 230, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_current, "Model: " + config.getModelText(), (10, h-60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_current, "Updated at: " + config.getModelUpdatedAtText(), (10, h-40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame_current, "Detector: " + config.getDetectorURL(), (10, h-20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)

    def hconcatResizeMin(self, frames, interpolation=cv2.INTER_CUBIC):
        hMin = min(frame.shape[0] for frame in frames)
        framesResize = [cv2.resize(frame, (int(frame.shape[1] * hMin / frame.shape[0]), hMin), interpolation=interpolation) for frame in frames]
        return cv2.hconcat(framesResize)

    def vconcatResizeMin(self, frames, interpolation=cv2.INTER_CUBIC):
        wMin = min(frame.shape[1] for frame in frames)
        framesResize = [cv2.resize(frame, (wMin, int(frame.shape[0] * wMin / frame.shape[1])), interpolation=interpolation) for frame in frames]
        return cv2.vconcat(framesResize) 

    def getInferenceDataJSON(self, config, inference_interval, entities_dict, video_sources):
        entities = []
        for key in entities_dict:
            entity_dict = {}
            entity_dict["eclass"] = key
            entity_dict["details"] = entities_dict[key]
            entities.append(entity_dict)

        ncols = config.getViewColumn()
        nsrc = len(video_sources)
        nrows = math.trunc((nsrc-1) / ncols) + 1
        rowFrames = []
        for r in range (0, nrows):
            colFrames = []
            for c in range(0, ncols):
                v = r * ncols + c
                if v < nsrc:
                    videoSource = video_sources[v]
                    if videoSource.frame_annotated is not None:
                        colFrames.append(videoSource.frame_annotated)
                    else:
                        if videoSource.getResolution() is not None:
                            colFrames.append(cv2.resize(config.getBlankFrame(), videoSource.getResolution()))
                        else:
                            colFrames.append(config.getBlankFrame())
                else:
                    colFrames.append(config.getBlankFrame())

            hframe = self.hconcatResizeMin(colFrames, interpolation=cv2.INTER_CUBIC)
            rowFrames.append(hframe)

        fullFrame = self.vconcatResizeMin(rowFrames, interpolation=cv2.INTER_CUBIC)

        bgColor = [15, 15, 15]
        fullFrame = cv2.copyMakeBorder(fullFrame, 0, 60, 0, 0, cv2.BORDER_CONSTANT, value=bgColor)

        status_text = "Overlay: "
        if config.shouldShowOverlay():
            status_text += "YES"
        else:
           status_text += "NO "

        if ncols == 1:
            font_scale = 1
            status_x = 60
        else:
            font_scale = 1.5
            ht, wd, ch = fullFrame.shape
            status_x = int((wd - 1080)/2)

        alpha = 0.7
        status = fullFrame.copy()
        h, w = fullFrame.shape[:2]
        cv2.rectangle(status, (2, h-28), (w-2, h-2), (64, 64, 64), -1)
        cv2.addWeighted(status, alpha, fullFrame, 1 - alpha, 0, fullFrame)
        cv2.putText(fullFrame, status_text, (status_x, h-5), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 192), 1, cv2.LINE_AA)

        retval, buffer = cv2.imencode('.jpg', fullFrame)

        infered_b64_frame = (base64.b64encode(buffer)).decode('utf8')
            
        # Create inference payload
        inference_dict = {}
        inference_dict['deviceid'] = config.getDeviceId()
        inference_dict['devicename'] = config.getDeviceName()
        inference_dict['tool'] = config.getTool()
        inference_dict['date'] = int(time.time())
        inference_dict['camtime'] = 0
        inference_dict['time'] = round(inference_interval, 3)
        inference_dict['count'] = len(entities)
        inference_dict['entities'] = entities
        inference_dict['image'] = infered_b64_frame

        inference_data = {}
        inference_data['detect'] = inference_dict
        inference_data_json = json.dumps(inference_data);

        return inference_data_json
