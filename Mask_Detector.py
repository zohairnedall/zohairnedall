import tensorflow as tf
import imutils
import numpy as np
import cv2
import os
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50)
GPIO.setup(12,GPIO.OUT)
servo2 = GPIO.PWM(12,50)
servo1.start(0)
servo2.start(0)
def detect_and_predict_mask(frame,faceNet,maskNet):
    
    (h,w)=frame.shape[:2]
    blob=cv2.dnn.blobFromImage(frame,1.0,(300,300),(104.0,177.0,123.0))
    
    faceNet.setInput(blob)
    detections=faceNet.forward()
    
    
    faces=[]
    locs=[]
    preds=[]
    
    
    for i in range(0,detections.shape[2]):
        confidence=detections[0,0,i,2]
    
    
        if confidence>0.5:
        
            box=detections[0,0,i,3:7]*np.array([w,h,w,h])
            (startX,startY,endX,endY)=box.astype('int')
        
        
            (startX,startY)=(max(0,startX),max(0,startY))
            (endX,endY)=(min(w-1,endX), min(h-1,endY))
        
            
            face=frame[startY:endY, startX:endX]
            face=cv2.cvtColor(face,cv2.COLOR_BGR2RGB)
            face=cv2.resize(face,(224,224))
            face=img_to_array(face)
            face=preprocess_input(face)
        
            faces.append(face)
            locs.append((startX,startY,endX,endY))
        
        
        if len(faces)>0:
            faces=np.array(faces,dtype='float32')
            preds=maskNet.predict(faces,batch_size=12)
        
        return (locs,preds)



prototxtPath=os.path.sep.join([r'/home/pi/project','deploy.prototxt'])
weightsPath=os.path.sep.join([r'/home/pi/project','res10_300x300_ssd_iter_140000.caffemodel'])


faceNet=cv2.dnn.readNet(prototxtPath,weightsPath)


maskNet=load_model(r'/home/pi/project/mobilenet_v2.model')


vs=VideoStream(src=0).start()
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
while True:
    
    frame=vs.read()
    frame=imutils.resize(frame,width=400)
    
    
    (locs,preds)=detect_and_predict_mask(frame,faceNet,maskNet)
    
    
    
    for (box,pred) in zip(locs,preds):
        (startX,startY,endX,endY)=box
        (mask,withoutMask)=pred
        
        
        if mask>withoutMask:
            label='Mask'
            
            motor = '1'

        else:
            label='No Mask'
            motor='2'
            
        
        
            
        color=(0,255,0) if label=='Mask' else (0,0,255)
        
        
        cv2.putText(frame,label,(startX,startY-10),cv2.FONT_HERSHEY_SIMPLEX,0.45,color,2)
        
        cv2.rectangle(frame,(startX,startY),(endX,endY),color,2)
        
        while True:
            if motor=='1':
                servo1.ChangeDutyCycle(12)
                servo2.ChangeDutyCycle(2)
                time.sleep(1)
                servo1.ChangeDutyCycle(0)
                servo2.ChangeDutyCycle(0)
                time.sleep(3)
                servo1.ChangeDutyCycle(2)
                servo2.ChangeDutyCycle(12)
                time.sleep(1)
                servo1.ChangeDutyCycle(0)
                servo2.ChangeDutyCycle(0)
                time.sleep(3)
                motor='5'
            else:
                break
            
        
        

    cv2.imshow("Frame",frame)
    key=cv2.waitKey(1) & 0xFF
    
    
    
    if key==ord('q'):
        break
    
servo1.stop()
servo2.stop()
GPIO.cleanup()
print ("Goodbye")
cv2.destroyAllWindows()
vs.stop()
        
  


