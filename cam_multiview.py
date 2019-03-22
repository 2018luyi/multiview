import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

a, test = cap.read()

selection = 0

w_size = test.shape[1]
h_size = test.shape[0]

img_size = [w_size, h_size]

cv2.namedWindow('frame')

refPt = []

def mouse_callback(event, x, y, flags, param):
    global refPt, selection

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [x, y]

        if selection == 0:
            if refPt[0] < img_size[0] and refPt[1] < img_size[1]:
                selection = 1

            elif refPt[0] >= img_size[0] and refPt[1] < img_size[1]:
                selection = 2

            elif refPt[0] < img_size[0] and refPt[1] >= img_size[1]:
                selection = 3

            elif refPt[0] >= img_size[0] and refPt[1] >= img_size[1]:
                selection = 4

        else: selection = 0

        print(refPt)

cv2.setMouseCallback('frame', mouse_callback)

while(True):

    # Capture frame-by-frame
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()
    frame3 = frame
    frame4 = frame2
    
    # Merge
    vis1 = np.concatenate((frame, frame2), axis=1)
    vis2 = np.concatenate((frame3, frame4), axis=1)
    vis = np.concatenate((vis1,vis2), axis=0)
    
    
    # Display the resulting frame
    if selection == 0:
        cv2.imshow('frame', vis)

    elif selection == 1:
        big_img = cv2.resize(frame, None, fx=2.0, fy=2.0)
        cv2.imshow('frame', big_img)

    elif selection == 2:
        big_img = cv2.resize(frame2, None, fx=2.0, fy=2.0)
        cv2.imshow('frame', big_img)

    elif selection == 3:
        big_img = cv2.resize(frame3, None, fx=2.0, fy=2.0)
        cv2.imshow('frame', big_img)

    elif selection == 4:
        big_img = cv2.resize(frame4, None, fx=2.0, fy=2.0)
        cv2.imshow('frame', big_img)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.getWindowProperty('frame',cv2.WND_PROP_VISIBLE) < 1:
        break

# When everything done, release the capture
cap.release()
cap2.release()
cv2.destroyAllWindows()
