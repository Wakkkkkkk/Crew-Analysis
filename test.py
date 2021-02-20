import cv2
import numpy as np

cap = cv2.VideoCapture("rowingfromabove.mp4")
#https://docs.opencv.org/3.4/da/d97/tutorial_threshold_inRange.html
#https://pythonprogramming.net/color-filter-python-opencv-tutorial/
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_image_display/py_image_display.html
#https://stackoverflow.com/questions/58896805/using-a-mask-transparent-pixel-alpha-for-template-matching-in-opencv

while(1):
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_red = np.array([30,150,50])
    upper_red = np.array([255,255,180])
    
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(frame,frame, mask= mask)

    #cv2.imshow('frame',frame)
    #cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()