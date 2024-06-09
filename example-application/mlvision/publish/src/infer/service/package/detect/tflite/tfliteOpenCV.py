#
# tfliteOpenCV.py
#

import cv2
import datetime

from package.detect.baseOpenCV import BaseOpenCV

class TFLiteOpenCV(BaseOpenCV):
    def __init__(self):
        super().__init__()
    
    def annotateFrame(self, config, labels, frame_current, src_name, frame_faces, frame_gray, boxes, classes, scores):
        entities_dict = {}
        for i in range(len(scores)):
            if ((scores[i] > config.getMinConfidenceThreshold()) and (scores[i] <= 1.0)):
                
                imageH, imageW, _ = frame_current.shape

                # Get bounding box coordinates and draw box
                ymin = int(max(1, (boxes[i][0] * imageH)))
                xmin = int(max(1, (boxes[i][1] * imageW )))
                ymax = int(min(imageH, (boxes[i][2] * imageH)))
                xmax = int(min(imageW, (boxes[i][3] * imageW)))
                cv2.rectangle(frame_current, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

                # Draw label
                object_name = labels[int(classes[i])]
                label = '%s: %d%%' % (object_name,  int(scores[i] * 100))
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                label_ymin = max(ymin, labelSize[1] + 8)
                cv2.rectangle(frame_current, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
                cv2.putText(frame_current, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
                details = []
                if object_name in entities_dict:
                    details = entities_dict[object_name]
                else:
                    entities_dict[object_name] = details

                h = int(ymax-ymin)
                w = int(xmax-xmin)
                detail_dict = {}
                detail_dict['h'] = h 
                detail_dict['w'] = w
                detail_dict['cx'] = int(xmin + w/2)
                detail_dict['cy'] = int(ymin + h/2)
                detail_dict['confidence'] = float('{0:.2f}'.format(scores[i]))
                details.append(detail_dict)

                if frame_faces is not None:
                    for (x, y, w, h) in frame_faces:
                        if config.shouldBlurFace():
                            cv2.ellipse(frame_current, (int(x + w/2), int(y + h/2)), (int(0.6 * w), int(0.8 * h)), 0, 0, 360, (128, 128, 128), -1)
                        elif config.shouldDetectFace():
                            cv2.rectangle(frame_current, (x, y), (x+w, y+h), (192, 192, 192), 2)
                            roi_gray = frame_gray[y:y+h, x:x+w]
                            roi_color = frame_current[y:y+h, x:x+w]
                            eyes = self.eye_cascade.detectMultiScale(roi_gray)
                            for (ex, ey, ew, eh) in eyes:
                                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (64, 128, 192), 2)

        super().addStatus(config, frame_current, src_name)

        return entities_dict 
        
