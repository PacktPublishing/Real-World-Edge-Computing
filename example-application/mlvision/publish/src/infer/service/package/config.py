#
# config.py
#

from threading import Thread

import numpy 
import cv2
import datetime
import json
import os
import requests
import time
import zipfile
import shutil

class Config:
    def __init__(self, fmwk, framerate=30):
        self.fmwk = fmwk
        self.framerate = framerate

        # seed resolution for blankFrame to be used as base blankFrame
        resolution = (640, 480)
        b_frame_border = 8
        bg_color = [32, 32, 32]
        b_frame = numpy.zeros([resolution[1] - 2 * b_frame_border, resolution[0] - 2 * b_frame_border, 3], dtype=numpy.uint8)
        b_frame[:] = (48, 48, 48) # gray fill
        self.blankFrame = cv2.copyMakeBorder(b_frame, b_frame_border, b_frame_border, b_frame_border, b_frame_border, cv2.BORDER_CONSTANT, value=bg_color)
        
        self.env_dict = {}
        self.env_dict['SHOW_OVERLAY'] = os.environ['SHOW_OVERLAY'] if 'SHOW_OVERLAY' in os.environ else True
        self.env_dict['PUBLISH_STREAM'] = os.environ['PUBLISH_STREAM'] if 'PUBLISH_STREAM' in os.environ else True

        self.mms_polling_interval = os.environ['MMS_POLLING_INTERVAL'] if 'MMS_POLLING_INTERVAL' in os.environ else 10

        self.modelFmwk = None
        self.modelDir = None

        self.modelObjectType = None
        self.modelObjectId = None
        self.modelNet = None
        self.modelVersion = None

        self.modelUpdatedAt = datetime.datetime.now()
        self.reloadTFLiteModel = False
        self.detectorInitialized = False

        if self.getIsTFLite():
            self.setTFLiteDefaults()

        print ("{:.7f} Config initialized".format(time.time()))

    def setDetectorInitialized(self, flag):
        self.detectorInitialized = flag

    def getDetectorInitialized(self):
        return self.detectorInitialized
        
    def getIsTFLite(self):
        return self.fmwk == 'tflite'

    # os.path.join - leading / only for the first path. NO leading / in sub paths
    def setTFLiteDefaults(self):
        self.detectTFLite = "detect.tflite"
        self.labelmap = "labelmap.txt"
        self.tool = "TensorFlow Lite OpenCV"
        self.modelTFLite = None
        self.defaultModelDir = os.environ['APP_MODEL_DIR']
        self.defaultModelTFLite = "default-" + os.environ['APP_ML_MODEL']
        self.modelObjectId = self.defaultModelTFLite
        with zipfile.ZipFile(os.path.join(self.defaultModelDir, self.defaultModelTFLite), 'r') as zip_ref:
            zip_ref.extractall(self.defaultModelDir)
            zip_ref.close()

    def getObjectName(self):
        return self.objectName

    def getModelDir(self):
        return self.defaultModelDir if self.modelDir is None else self.modelDir

    def getModelTFLite(self):
        return self.defaultModelTFLite if self.modelTFLite is None else self.modelTFLite

    def getLabelmap(self):
        return self.labelmap

    def getModelPathTFLite(self):
        return os.path.join(self.getModelDir(), self.detectTFLite)

    def getLabelmapPath(self):
        return os.path.join(self.getModelDir(), self.getLabelmap())

    def getModelPathTFLiteUpdate(self):
        return os.path.join(self.modelDirTFLiteUpdateNextV12, self.detectTFLite)

    def getLabelmapPathUpdate(self):
        return os.path.join(self.modelDirTFLiteUpdateNextV12, self.getLabelmap())

    #cycle v1 or v2
    def getModelDirTFLiteUpdateNext(self):
        if os.path.exists(os.path.join(self.getModelDir(), "v1", self.detectTFLite)):
            shutil.rmtree(os.path.join(self.getModelDir(), "v1"))
            vDir = os.path.join(self.getModelDir(), "v2")
            os.makedirs(vDir)
            return vDir
        else:
            if os.path.exists(os.path.join(self.getModelDir(), "v2", self.detectTFLite)):
                shutil.rmtree(os.path.join(self.getModelDir(), "v2"))
            vDir = os.path.join(self.getModelDir(), "v1")
            os.makedirs(vDir)
            return vDir
            
    def getAppCameras(self, limit):
        if 'APP_CAMERAS' in os.environ:
            if os.environ['APP_CAMERAS'] == '-':
                return None
            elif os.environ['APP_CAMERAS'] == 'all':
                return self.discoverVideoDeviceSources(limit)
            else:
                deviceSources = []
                sources =  (os.environ['APP_CAMERAS'].replace(" ", "")).split(",")
                for source in sources:
                    vcap = cv2.VideoCapture(int(source))
                    if vcap.read()[0]:
                        deviceSources.append(int(source))
                        vcap.release()
                    time.sleep(1) 
                return deviceSources
        else:
            return None

    def getVideoFiles(self):
        videoFilesStr = ''
        if 'APP_VIDEO_FILES' in os.environ:
            if os.environ['APP_VIDEO_FILES'] == '-':
                videoFilesStr = ''
            else:
                videoFilesStr = os.environ['APP_VIDEO_FILES']
        else:
            videoFilesStr = ''

        videoFiles = (videoFilesStr.replace(" ", "")).split(",")
        videoFile = [videoFile for videoFile in videoFiles if len(videoFile) > 0]
        return videoFiles if videoFile else None

    def getRTSPStreams(self):
        rtspStr = ''
        if 'APP_RTSPS' in os.environ:
            if os.environ['APP_RTSPS'] == '-':
                rtspStr = ''
            else:
                rtspStr = os.environ['APP_RTSPS'] 
        else:
            rtspStr = ''

        rtsps = (rtspStr.replace(" ", "")).split(",")
        rtsp = [rtsp for rtsp in rtsps if "rtsp" in rtsp]  
        return rtsps if rtsp else None

    def getRTSPIP(self, rtsp):
        x = rtsp.split(":")
        x = x[1].strip("/")
        return x

    def getViewColumn(self):
        return int(os.environ['APP_VIEW_COLUMNS'] if 'APP_VIEW_COLUMNS' in os.environ else '1')

    def getBlankFrame(self):
        return self.blankFrame

    def discoverVideoDeviceSources(self, limit):
        deviceSources = []
        for source in range(0, limit):
            vcap = cv2.VideoCapture(source)
            if vcap.read()[0]:
                deviceSources.append(source)
                vcap.release()
                time.sleep(1) 

        return deviceSources

    def getDeviceId(self):
        return os.environ['DEVICE_ID'] if 'DEVICE_ID' in os.environ else 'DEVICE_ID'
    
    def getDeviceName(self):
        return os.environ['DEVICE_NAME'] if 'DEVICE_NAME' in os.environ else 'DEVICE_NAME'
    
    def getPublishPayloadStreamUrl(self):
        if self.getIsTFLite():
            return os.environ['HTTP_PUBLISH_STREAM_URL'] if 'HTTP_PUBLISH_STREAM_URL' in os.environ else 'Missing HTTP_PUBLISH_STREAM_URL'
        else: #network = host vino
            return "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":5000/publish/stream"
            
    def getMinConfidenceThreshold(self):
        return float(os.environ['MIN_CONFIDENCE_THRESHOLD'] if 'MIN_CONFIDENCE_THRESHOLD' in os.environ else "0.6")

    def shouldShowOverlay(self):
        return self.env_dict['SHOW_OVERLAY'] == 'true'

    def shouldPublishStream(self):
        return self.env_dict['PUBLISH_STREAM'] == 'true'
    
    def getFramerate(self):
        return self.framerate

    def getTool(self):
        return self.tool

    def getInputMean(self):
        return 127.5

    def getInputStd(self):
        return 127.5

    def getModelText(self):
        return self.modelObjectId 

    def getModelUpdatedAtText(self):
        return self.modelUpdatedAt.strftime("%Y-%m-%d %H:%M:%S")
    
    def getDetectorURL(self):
        return "Internal"

    # uses network:host . Use host network IP
    def getMMSModelProviderUrl(self):
        return "http://" + os.environ['DEVICE_IP_ADDRESS'] + ":7772/mmsmodel"

    #{'mms_action': 'updated', 'value': [{'OBJECT_TYPE': 'mmsmodel', 'OBJECT_ID': 'tflite-model-1.0.1-mms.zip', 'MODEL_NET': 'ssd_mobilenet_v1_1.0_quant', 'MODEL_FMWK': 'tflite', 'MODEL_VERSION': '1.0.1', 'MODEL_DIR': '/var/local/horizon/ml/model/tflite'}]}'
    def mmsModel(self):
        url = self.getMMSModelProviderUrl()
        print ("{:.7f} mmsModel: url ".format(time.time()), url, end="\n", flush=True)
        try:
            resp = requests.get(url)
            dict = resp.json()
            print ("{:.7f} mmsModel: dict ".format(time.time()), dict, end="\n", flush=True)
            if dict['mms_action'] == 'updated':
                value_list = dict['value']
                for value_dict in value_list:
                    print ("{:.7f} mmsModel: value_dict ".format(time.time()), value_dict, end="\n", flush=True)
                    self.modelUpdatedAt = datetime.datetime.now()
                    if self.getIsTFLite():
                        self.modelObjectType = value_dict['OBJECT_TYPE']
                        self.modelTFLite = "mmsmodel-" + value_dict['OBJECT_ID']
                        self.modelObjectId = value_dict['OBJECT_ID']
                        self.modelNet = value_dict['MODEL_NET']
                        self.modelFmwk = value_dict['MODEL_FMWK']
                        self.modelVersion = value_dict['MODEL_VERSION']
                        self.modelDir = value_dict['MODEL_DIR']
                        self.modelDirTFLiteUpdateNextV12 = self.getModelDirTFLiteUpdateNext()

                        with zipfile.ZipFile(os.path.join(self.modelDir, self.modelTFLite), 'r') as zip_ref:                            
                            zip_ref.extractall(self.modelDirTFLiteUpdateNextV12)
                            zip_ref.close()
                            self.setReloadTFLiteModel(True)
                            
        except requests.exceptions.HTTPError as errh:
            print ("{:.7f}V mmsModel: Http Error".format(time.time()), errh, end="\n", flush=True)
        except requests.exceptions.ConnectionError as errc:
            print ("{:.7f}V mmsModel: Http Error".format(time.time()), errc, end="\n", flush=True)
            None
        except requests.exceptions.Timeout as errt:
            print ("{:.7f}V mmsModel: Timeout".format(time.time()), errt, end="\n", flush=True)
        except requests.exceptions.RequestException as err:
            print ("{:.7f}V mmsModel: Other Error".format(time.time()), err, end="\n", flush=True)

    def mmsModelProcessor(self, interval):
        while True:
            print ("{:.7f} mmsModelProcessor: polling at interval ".format(time.time()), interval, end="\n", flush=True)
            time.sleep(int(interval))
            if self.getDetectorInitialized():
                self.mmsModel()

    def mmsPoller(self):
        Thread(target=self.mmsModelProcessor, args=(self.mms_polling_interval,)).start()

    def getReloadTFLiteModel(self):
        return self.reloadTFLiteModel

    def setReloadTFLiteModel(self, flag):
        self.reloadTFLiteModel = flag

