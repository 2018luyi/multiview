import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(2)
cap3 = cv2.VideoCapture(4)
cap4 = cv2.VideoCapture(6)

w_size = 640
h_size = 360
img_size = [w_size, h_size]

cap.set(cv2.CAP_PROP_FRAME_WIDTH, w_size)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h_size)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, w_size)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, h_size)
cap3.set(cv2.CAP_PROP_FRAME_WIDTH, w_size)
cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, h_size)
cap4.set(cv2.CAP_PROP_FRAME_WIDTH, w_size)
cap4.set(cv2.CAP_PROP_FRAME_HEIGHT, h_size)




cv2.namedWindow('frame')

refPt = []

selection = 0

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
    #ret, frame = cap.read()
    #ret2, frame2 = cap2.read()
    #ret3, frame3 = cap3.read()
    #ret4, frame4 = cap4.read()
    
    f_test = {}
    _, f_test[0] = cap.read()
    _, f_test[1] = cap2.read()
    _, f_test[2] = cap3.read()
    _, f_test[3] = cap4.read()
    
    frame = f_test[0]
    frame2 = f_test[1]
    frame3 = f_test[2]
    frame4 = f_test[3]
    
    # Merge
    txt_frame = np.zeros((60,1280,3), np.uint8)
    vis1 = np.concatenate((frame, frame2), axis=1)
    vis2 = np.concatenate((frame3, frame4), axis=1)
    vis = np.concatenate((txt_frame,vis1,vis2), axis=0)
    
    
    #vis = np.concatenate((txt_frame,vis), axis=0)
    
    # text
    text = "한글"
    x=50
    h=100
    
    # For transparancy
    #vis_pil = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
    #vis_pil = Image.fromarray(vis_pil).convert('RGBA')
    #tr_txt = Image.new('RGBA', (vis.shape[1], vis.shape[0]), (255,255,255,0))

    #cv2.putText(vis, text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
    fontpath = "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"
    font = ImageFont.truetype(fontpath, 40)
    
    #dtxt = ImageDraw.Draw(tr_txt)
    #dtxt.text((x,h), text, font=font, fill=(255,255,255,80))
    #out = Image.alpha_composite(vis_pil, dtxt)
    
    #out = cv2.cvtColor(np.array(out), cv2.COLOR_RGB2BGR)
    
    img_pil = Image.fromarray(vis)
    draw = ImageDraw.Draw(img_pil)
    draw.text((x, h), text, font=font, fill=(255, 255, 255, 0))
    vis = np.array(img_pil)
    #vis = out
    
    
    # Display the resulting frame
    if selection == 0:
        #cv2.putText(vis, text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
        #img_pil = Image.fromarray(vis)
        #draw = ImageDraw.Draw(img_pil)
        #draw.text((x, h), text, font=font, fill=(255, 255, 255, 0))
        #vis = np.array(img_pil)
        cv2.imshow('frame', vis)
        
    elif selection == 1:
        big_img = cv2.resize(frame, None, fx=2.0, fy=2.0)
        #cv2.putText(big_img, text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
        img_pil = Image.fromarray(big_img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x, h), text, font=font, fill=(255, 255, 255, 0))
        big_img = np.array(img_pil)
        cv2.imshow('frame', big_img)

    elif selection == 2:
        big_img = cv2.resize(frame2, None, fx=2.0, fy=2.0)
        #cv2.putText(big_img, text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
        img_pil = Image.fromarray(big_img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x, h), text, font=font, fill=(255, 255, 255, 0))
        big_img = np.array(img_pil)
        cv2.imshow('frame', big_img)

    elif selection == 3:
        big_img = cv2.resize(frame3, None, fx=2.0, fy=2.0)
        #cv2.putText(big_img, text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
        img_pil = Image.fromarray(big_img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x, h), text, font=font, fill=(255, 255, 255, 0))
        big_img = np.array(img_pil)
        cv2.imshow('frame', big_img)

    elif selection == 4:
        big_img = cv2.resize(frame4, None, fx=2.0, fy=2.0)
        #cv2.putText(big_img, text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
        img_pil = Image.fromarray(big_img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x, h), text, font=font, fill=(255, 255, 255, 0))
        big_img = np.array(img_pil)
        cv2.imshow('frame', big_img)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.getWindowProperty('frame',cv2.WND_PROP_VISIBLE) < 1:
        break

# When everything done, release the capture
cap.release()
cap2.release()
cap3.release()
cap4.release()
cv2.destroyAllWindows()
