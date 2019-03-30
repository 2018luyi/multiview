
import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image, ImageColor
import can
from threading import Thread
import time
import matplotlib.pyplot as plt

TXT_WHT = (255,255,255,255)
TXT_BLU = (255,0,0,255)
TXT_RED = (0,0,255,255)
TXT_GRN = (0,255,0,255)
TXT_WHT50 = (255,255,255,128)
TXT_WHT25 = (255,255,255,64)
TXT_WHT75 = (255,255,255,192)
TXT_ORG = (0,128,255,255)

# CAN MASK
# 0b0111111111110000

class multiView:
    def __init__(self, vid_num=[0, 2, 4, 6], can_chan='can0', vid_res=[640, 480],
                 win_n='MultiView', can_filter=[{"can_id": 0x19ffa050, "can_mask": 0x1FFFFF00, "extended": True}]):
        self.vid = vid_num
        self.can_c = can_chan
        self.vid_res = vid_res
        
        self.cap = {}
        self.selection = 0
        self.guiMode = 0
        
        self.vid_thread = None
        self.can_thread = None
        
        self.can_filter = can_filter
        self.can_data = ["", 0, 0, 0, 0, 0]
        
        #self.fontpath = "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf" NanumSquareBold.ttf
        self.fontpath = "/Library/Fonts/NanumSquareBold.ttf"
        self.font1 = ImageFont.truetype(self.fontpath, 30)
        self.font2 = ImageFont.truetype(self.fontpath, 40)
        
        self.win_name = win_n
        
        self.resizing = [(1200, 900), (400, 300)]
                
        # Calculating FPS
        self.preTime = 0
        
        # Close flag
        self.isClose = False
        
        
        # Text position predefine
        # For steering
        initx = 70
        inity = 5
        int1 = 30
        int2 = 120
        self.stPos = {}
        self.stTxt = "좌                           조향                           우"
        self.stTxtPos = (25, 10)
        for i in range(10):
            self.stPos[i] = (initx+(int1*i), inity)
            if i >= 5:
                self.stPos[i] = (initx+(int1*(i-1))+int2, inity)

        ypos = 10
        self.txtPos = [(660, ypos), (860, ypos), (1060, ypos), (1150, ypos)]

        
        # Open webcams
        #fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        for i in range(len(self.vid)):
            self.cap[i] = cv2.VideoCapture(self.vid[i])
            if self.cap[i].isOpened() is False:
                print("Error: /dev/video%d is not opened. Please check connection."%self.vid[i])
                return -1
            #self.cap[i].set(cv2.CAP_PROP_FOURCC, fourcc)
            self.cap[i].set(cv2.CAP_PROP_FRAME_WIDTH, self.vid_res[0])
            self.cap[i].set(cv2.CAP_PROP_FRAME_HEIGHT, self.vid_res[1])
            #self.cap[i].set(cv2.CAP_PROP_FPS, 60)
            
        

        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            refPt = [x, y]

            if self.selection == 0:
                if refPt[0] < self.vid_res[0] and refPt[1] < self.vid_res[1]:
                    self.selection = 1

                elif refPt[0] >= self.vid_res[0] and refPt[1] < self.vid_res[1]:
                    self.selection = 2

                elif refPt[0] < self.vid_res[0] and refPt[1] >= self.vid_res[1]:
                    self.selection = 3

                elif refPt[0] >= self.vid_res[0] and refPt[1] >= self.vid_res[1]:
                    self.selection = 4

            else: self.selection = 0

            #print(refPt, self.selection)


            
    def vidThreadStart(self):
        if self.vid_thread == None:
            self.vid_thread = Thread(target=self.videoShowThread)
            self.vid_thread.start()
            self.preTime = time.time()
  


    def canThreadStart(self):
        # Open CAN bus
        self.bus = can.Bus(interface='socketcan', channel=self.can_c)
        # Setting filters
        self.bus.set_filters(self.can_filter)
        if self.can_thread == None:
            self.can_thread = Thread(target=self.canReadThread)
            self.can_thread.start()

            
            
    def videoShowThread(self):
        while(self.isClose==False):
            # FPS
            fps = 1.0/(time.time() - self.preTime)
            self.preTime = time.time()
            
            """
            vid_frame = {}
            
            for i in range(len(self.vid)):
                _, vid_frame[i] = self.cap[i].read()
            """
            
            vid_frame = {}
            _, vid_frame[0] = self.cap[0].read()
            vid_frame[1] = vid_frame[0]
            vid_frame[2] = vid_frame[0]
            vid_frame[3] = vid_frame[0]
            
            if self.selection == 0:
                # Merging
                upper_frame = np.concatenate((vid_frame[0], vid_frame[1]), axis=1)
                lower_frame = np.concatenate((vid_frame[2], vid_frame[3]), axis=1)
                total_frame = np.concatenate((upper_frame, lower_frame), axis=0)
                
            elif self.selection == 1:
                total_frame = cv2.resize(vid_frame[0], None, fx=2.0, fy=2.0)
                
            elif self.selection == 2:
                total_frame = cv2.resize(vid_frame[1], None, fx=2.0, fy=2.0)
                
            elif self.selection == 3:
                total_frame = cv2.resize(vid_frame[2], None, fx=2.0, fy=2.0)
                
            elif self.selection == 4:
                total_frame = cv2.resize(vid_frame[3], None, fx=2.0, fy=2.0)
                
            
            # Merging text part (upper bar)
            text_frame = np.zeros((60, self.vid_res[0]*2, 3), np.uint8)
            show_frame = np.concatenate((text_frame, total_frame), axis=0)
            
            
            
            # Text
            
            text_list = ["%s RPM"%"{:,}".format(self.can_data[3]), "리프트:  %d%%"%self.can_data[4], "연료:", "%d"%self.can_data[5]]

 
            # Text Color
            fuelCol = TXT_WHT
            if (self.can_data[5] <= 20): fuelCol = TXT_RED
            else: fuelCol = TXT_WHT
            
            # Text Font
            
            # Drawing Text
            frame_pil = Image.fromarray(show_frame).convert('RGBA')
            txt_new = Image.new('RGBA', frame_pil.size, (255,255,255,0))
            d_txt = ImageDraw.Draw(txt_new)
            
            
            # Steering part
            s_cmap = [TXT_WHT25] * 11
            s_cmap[self.can_data[2]] = TXT_ORG
            
            d_txt.text(self.stTxtPos, self.stTxt, font=self.font1, fill=TXT_WHT)
            for i in range(len(s_cmap)-1):
                d_txt.text(self.stPos[i], "█", font=self.font2, fill=s_cmap[i+1])
                

            d_txt.text(self.txtPos[0], text_list[0], font=self.font1, fill=TXT_WHT)
            d_txt.text(self.txtPos[1], text_list[1], font=self.font1, fill=TXT_WHT)
            d_txt.text(self.txtPos[2], text_list[2], font=self.font1, fill=TXT_WHT)
            d_txt.text(self.txtPos[3], text_list[3], font=self.font1, fill=fuelCol)
            frame_pil = Image.alpha_composite(frame_pil, txt_new)
            #draw = ImageDraw.Draw(frame_pil)
            #draw.text(t2Pos, text2, font=font, fill=t2Col)
            #draw.text(t3Pos, text3, font=font, fill=t3Col)

            show_frame = np.array(frame_pil)
            
            plt.axis("off")
            plt.imshow(cv2.cvtColor(show_frame, cv2.COLOR_BGR2RGB))
            plt.show()
            #cv2.imshow(self.win_name, show_frame)
            #cv2.setMouseCallback(self.win_name, self.mouse_callback)
            
            
            # Keyboard input
            # View change
            if cv2.waitKey(1) & 0xFF == ord('v'):
                self.guiMode += 1
                
                if self.guiMode >= 5: self.guiMode = 0
                    
                print(self.guiMode)
            
            # Quit GUI
            """
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.isClose = True
                break

            if cv2.getWindowProperty(self.win_name,cv2.WND_PROP_VISIBLE) < 1:
                self.isClose = True
                break
            """
                
        # Video releasing (out of while loop)
        for i in range(len(self.vid)):
            self.cap[i].release()
            
        # Close GUI
        cv2.destroyAllWindows()
                

            
    def canReadThread(self):
        while(self.isClose == False):
            raw_data = self.bus.recv().data
            
            if (raw_data[0] & 0b00000011 == 0):
                autoMode = "Off"
            elif (raw_data[0] & 0b00000011 == 1):
                autoMode = "경심"
            elif (raw_data[0] & 0b00000011 == 2):
                autoMode = "견인"
            elif (raw_data[0] & 0b00000011 == 3):
                autoMode = "위치"
                
            monitorMode = raw_data[0]>>5
            axleAngle = raw_data[1]
            engineRPM = raw_data[2] * 256 + raw_data[3]
            liftPos = raw_data[4]
            fuelLevel = raw_data[7]
            
            self.can_data = [autoMode, monitorMode, axleAngle, engineRPM, liftPos, fuelLevel]
                        
        # CAN bus closing (out of while loop)
        self.bus.shutdown()


        
def main():
    
    # Webcam number (for Logitech BRIO, 1 BRIO webcam has two /dev/videoXX, use first)
    #vid_num = [0, 2, 4, 6]
    vid_num = [0]
    # CAN channel
    can_ch = "can0"
    # Video resolution from webcam
    vid_res = [640, 480]
    # GUI window name
    win_n = "MultiView GUI"
    # CAN filter - CAN ID, MASK, EXTENDED
    # CAN ID input 0x19ffa050~0x19ffa05f
    can_filter=[{"can_id": 0x19ffa050, "can_mask": 0x1FFFFF00, "extended": True}]
    
    
    multiV = multiView(vid_num=vid_num, can_chan=can_ch, vid_res=vid_res, win_n=win_n, can_filter=can_filter)

    #multiV.canThreadStart()
    multiV.vidThreadStart()

    

if __name__ == '__main__':
    main()
    
