
import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image
import can
from threading import Thread
import time


class multiView:
    def __init__(self, vid_num=[0, 2, 4, 6], can_chan='can0', vid_res=[640, 480],
                 win_n='MultiView', can_filter=[{"can_id": 0x19ffa050, "can_mask": 0x1FFFFFFF, "extended": True}]):
        self.vid = vid_num
        self.can_c = can_chan
        self.vid_res = vid_res
        
        self.cap = {}
        self.selection = 0
        
        self.vid_thread = None
        self.can_thread = None
        
        self.can_filter = can_filter
        self.can_data = [0, 0, 0, 0, 0, 0]
        
        self.fontpath = "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"
        
        self.win_name = win_n
        #cv2.namedWindow(self.win_name)
        #cv2.setMouseCallback(self.win_name, self.mouse_callback)
        
        
        # Close flag
        self.isClose = False
        
        # Open webcams
        for i in range(len(self.vid)):
            self.cap[i] = cv2.VideoCapture(self.vid[i])
            if self.cap[i].isOpened() is False:
                print("Error: /dev/video%d is not opened. Please check connection."%self.vid[i])
                return -1
            
            self.cap[i].set(cv2.CAP_PROP_FRAME_WIDTH, self.vid_res[0])
            self.cap[i].set(cv2.CAP_PROP_FRAME_HEIGHT, self.vid_res[1])
            
        # Open CAN bus
        self.bus = can.Bus(interface='socketcan', channel=self.can_c)
        # Setting filters
        self.bus.set_filters(self.can_filter)
        

        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            refPt = [x, y]

            if self.selection == 0:
                if refPt[0] < self.vid_res[0] and refPt[1] < self.vid_res[1]:
                    self.selection = 1

                elif refPt[0] >= self.vid_res[0] and refPt[1] < self.vid_res[1]:
                    self.selection = 2

                elif refPt[0] < self.vid_res[0] and refPt[1] >= self.vid_rese[1]:
                    self.selection = 3

                elif refPt[0] >= self.vid_res[0] and refPt[1] >= self.vid_rese[1]:
                    self.selection = 4

            else: self.selection = 0

            print(refPt, self.selection)


            
    def vidThreadStart(self):
        if self.vid_thread == None:
            print("vid thread")
            self.vid_thread = Thread(target=self.videoShowThread)
            self.vid_thread.start()
  


    def canThreadStart(self):
        if self.can_thread == None:
            self.can_thread = Thread(target=self.canReadThread)
            self.can_thread.start()

            
            
    def videoShowThread(self):
        while(self.isClose==False):
            
            vid_frame = {}
            
            for i in range(len(self.vid)):
                _, vid_frame[i] = self.cap[i].read()
                
            
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
            
            # Drawing Text
            text = "한글 출력"
            position = (10, 30)
            font = ImageFont.truetype(self.fontpath, 40)
            frame_pil = Image.fromarray(show_frame)
            draw = ImageDraw.Draw(frame_pil)
            draw.text(position, text, font=font, fill=(255,255,255,0))
            show_frame = np.array(frame_pil)
            
            cv2.imshow(self.win_name, show_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.isClose = True
                break

            if cv2.getWindowProperty(self.win_name,cv2.WND_PROP_VISIBLE) < 1:
                self.isClose = True
                break
                
    
    def canReadThread(self):
        while(self.isClose == False):
            raw_data = self.bus.recv().data
            
            autoMode = raw_data[0] & 0b00000011
            monitorMode = raw_data[0]>>5
            axleAngle = raw_data[1]
            engineRPM = raw_data[2] * 256 + raw_data[3]
            liftPos = raw_data[4]
            fuelLevel = raw_data[7]
            
            self.can_data = [autoMode, monitorMode, axleAngle, engineRPM, liftPos, fuelLevel]
            
            
        
    
    
    def close(self):
        # Thread terminating
        self.vid_thread.join()
        self.can_thread.join()
        
        # Video releasing
        for i in range(len(self.vid)):
            self.cap[i].release()
        
        # CAN bus closing
        self.bus.shutdown()
        
        # Close GUI
        cv2.destroyAllWindows()



        
def main():
    
    # Webcam number (for Logitech BRIO, 1 BRIO webcam has two /dev/videoXX, use first)
    vid_num = [0, 2, 4, 6]
    # CAN channel
    can_ch = "can0"
    # Video resolution from webcam
    vid_res = [640, 480]
    # GUI window name
    win_n = "MultiView GUI"
    # CAN filter - CAN ID, MASK, EXTENDED
    can_filter=[{"can_id": 0x19ffa050, "can_mask": 0x1FFFFFFF, "extended": True}]
    
    
    multiV = multiView(vid_num=vid_num, can_chan=can_ch, vid_res=vid_res, win_n=win_n, can_filter=can_filter)
    
    print("main")
    #multiV.canThreadStart()
    multiV.vidThreadStart()
    
    
    #multiV.close()
    

if __name__ == '__main__':
    main()
    
