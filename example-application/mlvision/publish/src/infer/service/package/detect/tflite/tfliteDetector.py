#
# tfliteDetector.py
#

import importlib.util
import numpy
import time

class TFLiteDetector:
    def __init__(self, config, model=None):
        isTFLite = importlib.util.find_spec('tflite_runtime')
        if isTFLite:
            from tflite_runtime.interpreter import Interpreter

            if model == None:
                self.modelPath = config.getModelPathTFLite()
                #Fix label content
                with open(config.getLabelmapPath(), 'r') as f:
                    self.labels = [line.strip() for line in f.readlines()]
            else: 
                self.modelPath = config.getModelPathTFLiteUpdate()
                #Fix label content
                with open(config.getLabelmapPathUpdate(), 'r') as f:
                    self.labels = [line.strip() for line in f.readlines()]

            #Fix label content
            if self.labels[0] == '???':
                del(self.labels[0])

            print ("{:.7f} TFLiteDetector: self.modelPath: ".format(time.time()), self.modelPath, end="\n", flush=True)
            self.interpreter = Interpreter(model_path=self.modelPath)
            self.interpreter.allocate_tensors()

            self.inference_interval = 0

            print ("{:.7f} TFLiteDetector: init TFLite model ".format(time.time()), len(self.labels), end="\n", flush=True)

    def getModelPath(self):
        return self.modelPath

    def getLabels(self):
        return self.labels

    def infer(self, frame_normalized):
        t1 = time.time()
        self.interpreter.set_tensor(self.getInputDetailsIndex(), frame_normalized)
        self.interpreter.invoke()
        self.inference_interval = time.time() - t1
        return self.inference_interval

    def getInferenceInterval(self):
        return self.inference_interval

    def getInputDetailsIndex(self):
        return self.getInputDetails()[0]['index']

    def getInputDetails(self):
        return self.interpreter.get_input_details()

    def getOutputDetails(self):
        return self.interpreter.get_output_details()

    def getHeight(self):
        return self.getInputDetails()[0]['shape'][1]

    def getWidth(self):
        return self.getInputDetails()[0]['shape'][2]

    def getFloatingModel(self):
        return (self.getInputDetails()[0]['dtype'] == numpy.float32)

    def getResults(self):
        output_details = self.getOutputDetails()
        boxes = self.interpreter.get_tensor(output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(output_details[2]['index'])[0]
        num = self.interpreter.get_tensor(output_details[3]['index'])[0]

        return boxes, classes, scores, num

    def getInferResults(self, frame_normalized):
        inference_interval = self.infer(frame_normalized)
        boxes, classes, scores, num = self.getResults()
        return inference_interval, boxes, classes, scores
