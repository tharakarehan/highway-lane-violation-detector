import time
import cv2
import sys
import numpy as np
import argparse
import os
from utils import image_utils
from utils import compare
from utils.model_utils import vehicleDetector
from sort import Sort
from kalman_tracker import KalmanBoxTracker
import config
from shapely.geometry.polygon import Polygon

if "Tkinter" not in sys.modules:
    import tkinter as tk
    from tkinter import *
    from tkinter import messagebox
    from tkinter.filedialog import askopenfilename
    from tkinter.filedialog import askdirectory
from PIL import ImageTk, Image

In = False
Vid_path = None
Out_path = None
ldvar = False
playvar = False
m_width = 1000
m_height = 600

# Function to set focus
def focus1(event): 
    # set focus on the dur_field box 
    dur_field.focus_set()  
  
def focus2(event): 
    # set focus on the std_field box 
    std_field.focus_set()

def focus3(event): 
    # set focus on the thresh_field box 
    thresh_field.focus_set()

def input_path():
    global In
    global Vid_path
    In = True
    Vid_path = askopenfilename()
    print(Vid_path)
   

def output_path():
    global Out_path
    Out_path = askdirectory()
    # print(Out_path)

def playen():
    global playvar
    playvar = True

def loadmodel():
    global In
    global Vid_path
    global Out_path
    global vs
    global tracker
    global model 
    global W
    global H
    global ldvar
    global result
    global ratio
    
    if In and thresh_field.get() != "" and dur_field.get() != "" and std_field.get() != "":
        
        inputFile = Vid_path
        vs = cv2.VideoCapture(inputFile)
        fps = int(vs.get(cv2.CAP_PROP_FPS))
        (W, H) = (int(vs.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        print("Original FPS:", fps)

        Tr = float(thresh_field.get())
        length = int(float(dur_field.get()) * fps)
        std = float(std_field.get())
        tracker = Sort(length= length, std = std)
        KalmanBoxTracker.count = 0
        print(varck.get())
        if varck.get():
            if Out_path == None:
                Out_path = Vid_path[:-4]+'_saved.avi'
            result = cv2.VideoWriter(Out_path,  
                                    cv2.VideoWriter_fourcc(*'XVID'), 
                                    fps, (W,H))

        model = vehicleDetector(r'model\vehicle-detection-0202.xml', H, W, Tr)
        model.load()
        ldvar = True
        w_ratio = m_width/W
        h_ratio = m_height/H
        ratio = min(w_ratio,h_ratio)

        (grabbed, frame) = vs.read()
        if grabbed:
            frame1 = frame.copy()
            image_utils.draw_text(frame1, 'Draw dots on the right hand side line and press Enter', 
                                                                (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            config.right_pts, right_image = image_utils.get_points(frame,frame1,W,H)
            frame2 = right_image.copy()
            image_utils.draw_text(frame2, 'Draw dots on the middle line and press Enter', 
                                                                (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            config.middle_pts, middle_image = image_utils.get_points(right_image,frame2,W,H)
            frame3 = middle_image.copy()
            image_utils.draw_text(frame3, 'Draw dots on the left hand side line and press Enter', 
                                                                (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            config.left_pts, left_image = image_utils.get_points(middle_image,frame3,W,H)
            image_utils.draw_text(left_image, 'Drawing ground truths for lane is done. Press Enter to continue', 
                                                                (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            
            config.polygonR = Polygon(config.right_pts + config.middle_pts[: : -1])
            config.polygonL = Polygon(config.left_pts + config.middle_pts[: : -1])

            alpha = 0.15
            int_coords = lambda x: np.array(x).round().astype(np.int32)
            exteriorR = [int_coords(config.polygonR.exterior.coords)]
            exteriorL = [int_coords(config.polygonL.exterior.coords)]

            overlayR = left_image.copy()
            cv2.fillPoly(overlayR, exteriorR, color = (255, 81, 31))
            cv2.addWeighted(overlayR, alpha, left_image, 1 - alpha, 0, left_image)

            overlayL = left_image.copy()
            cv2.fillPoly(overlayL, exteriorL, color = (39, 237, 250))
            cv2.addWeighted(overlayL, alpha, left_image, 1 - alpha, 0, left_image)

            cv2.imshow("Image", left_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            
    else:
        messagebox.showerror(title="Message", message="No video selected or parameters are not given",icon='error')

def playvid():
    global In
    global Vid_path
    global Out_path
    global vs
    global tracker
    global model 
    global W
    global H
    global ldvar
    global result
    global ldvar
    global playvar
   
    if ldvar and playvar:
        
        (grabbed, frame) = vs.read()
        if grabbed:
            
            t1 = time.time()
            detections = model.predict(frame)
            trackers = tracker.update(detections, frame)
            t2 = time.time()
            latency = t2 - t1
            posList = []

            for dt in trackers:
                dt = dt.astype(np.int32)
                posList.append(compare.compare_pos(dt,W,H))
            # print(posList)
            frame = image_utils.draw_lanes(frame,config.right_pts,config.middle_pts,config.left_pts,W,H)
            ill_lane_count = 0
            parkCount = 0
            for idx, d in enumerate(trackers):
                d = d.astype(np.int32)
                frame, status = image_utils.draw_box(frame, d, W, H, idx, posList)
                if status == 'park':
                    parkCount += 1
                elif status == 'ill_lane':
                    ill_lane_count += 1

            frame = image_utils.draw_info(frame, latency, parkCount, ill_lane_count)

            if varck.get():
                result.write(frame)
            resized = cv2.resize(frame,(int(W*ratio),int(H*ratio)))
            frame = cv2.cvtColor(resized,cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            lvid.imgtk = imgtk
            lvid.configure(image=imgtk)
                        
        else:
            playvar = False
            if varck.get():
                result.release()

            vs.release()
    else:
        lvid.configure(text='Choose a video and play')
    lvid.after(1, playvid)
        

def stopvid():
    global playvar
    playvar = False
  

def Quit():
    gui.destroy()
    

gui = Tk() 
v1 = DoubleVar()
var1 = IntVar()

varck = IntVar()

gui.configure(background="light green") 
gui.title("Illegal Vehicle Parking Detection System") 
gui.geometry("1300x710")

Input = Button(gui, text="Input DIR", fg="Black",
                            command=input_path,height=2, width=19)
Input.place(x=111, y=30,anchor='c')
Output = Button(gui, text="Output DIR", fg="Black", 
                            command=output_path,height=2, width=19) 
Output.place(x=111, y=100,anchor='c')


#setting up labels for the text entry boxes
thresh_label = Label(gui, text="Detection Threshold", bg="light green",font=("Helvetica", 12)) 
thresh_label.place(x=111, y=160,anchor='c')
dur_label = Label(gui, text="Duration", bg="light green",font=("Helvetica", 12))
dur_label.place(x=70, y=240,anchor='c')
std_label = Label(gui, text="Standard Deviation", bg="light green",font=("Helvetica", 12))  
std_label.place(x=108, y=320,anchor='c')

#setting up text entry boxes
thresh_field = Entry(gui,width = 23)
thresh_field.place(x=111, y=200,anchor='c')
dur_field = Entry(gui,width = 23) 
dur_field.place(x=111, y=280,anchor='c')
std_field = Entry(gui,width = 23)
std_field.place(x=111, y=360,anchor='c')

thresh_field.bind("<Return>", focus1) 
dur_field.bind("<Return>", focus2)
std_field.bind("<Return>", focus3) 

Save = Checkbutton(gui, text="Save Video", variable=varck, 
                    bg='light green',font=("Helvetica", 10))
Save.place(x=111, y=404,anchor='c')

Load = Button(gui, text="Load", fg="Black",
                            command=loadmodel,height=2, width=19)
Load.place(x=111, y=460,anchor='c')

Play = Button(gui, text="Play", fg="Black",
                            command=playen,height=2, width=19)
Play.place(x=111, y=530,anchor='c')
Stop = Button(gui, text="Stop", fg="Black", 
                            command=stopvid,height=2, width=19) 
Stop.place(x=111, y=600,anchor='c')

Quit = Button(gui, text="Quit", fg="Black", 
                            bg = 'red',command=Quit,height=2, width=19) 
Quit.place(x=111, y=670,anchor='c')

lvid = Label(gui)
lvid.place(x=740, y=350,anchor='c')
playvid()

gui.mainloop()


