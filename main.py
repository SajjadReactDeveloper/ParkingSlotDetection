import cv2
import pickle
import cvzone
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://192.168.10.6:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cap = cv2.VideoCapture('geh.mp4');

available = set();

@app.get("/")
def read_root():
    with open('carParkPos', 'rb') as f:
        posList = pickle.load(f)

    #Width and Height of Rectangle
    width = 60
    height = 108

    def checkParkingSpace(imgProc):
        availableSpace = 0

        for i, pos in enumerate(posList):
            # print(posList)
            x,y = pos

            #crop image
            frame = imgProc[y:y+height, x:x+width]
            #cv2.imshow(str(x*y), frame)
            count = cv2.countNonZero(frame)

            if count < 2800:
                color = (0,255,0)
                thickness = 5
                availableSpace += 1
                cvzone.putTextRect(img, f'{str(i+1)}', (x, y+height-3), scale=1.5, thickness=2, offset=0, colorR=color)
                available.add(str(i+1))
                    
            else:
                color = (0,0,255)
                thickness = 2
                if str(i+1) in available:
                    available.remove(str(i+1))
                # available.remove(str(i+1))
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
            # cvzone.putTextRect(img, str(count), (x, y+height-3), scale=1.5, thickness=2, offset=0, colorR=color)

        cvzone.putTextRect(img, str(availableSpace), (100, 50), scale=3, thickness=5, offset=20)
        # print(available)
        @app.get("/booking/available")
        def read_root1():
            return {"Slots": available}


    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, img = cap.read();
        
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3,3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        checkParkingSpace(imgDilate)

        cv2.imshow("Image", img)
        cv2.waitKey(10)
