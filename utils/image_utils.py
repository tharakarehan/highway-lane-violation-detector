import cv2
import numpy as np
import config

def draw_box(frame, det, width, height, index, posList):
    status = 'empty'
    if (abs(det[2] - det[0]) > 0.04 * width) and (abs(det[3] - det[1]) > 0.04 * height) and (abs(det[2] - det[0]) < (3/4) * width) and (abs(det[3] - det[1]) < (3/4) * height):

        if (int(det[4]) == 0) :
            color = (0, 0, 255)
            text = 'Parked Illegally | id = {}'.format(det[5])
            text_scale = 0.2
            status = 'park'
        elif (posList[index]=='R' and posList.count('L')==0):
            color = (0,0,255)
            text = 'Improper Lane Usage  | id = {}'.format(det[5])
            text_scale = 0.2
            status = 'ill_lane'
        else:
            color = (0,255,0)
            text = 'id = {}'.format(det[5])
            text_scale = 0.4
            status = 'legit'

        cv2.rectangle(frame, (det[0], det[1]), (det[2], det[3]), color, 2)
        x, y = int((det[0]+det[2])/2),int((det[1]+det[3])/2)
        cv2.circle(frame,(x,y) ,radius= 2, color = color,thickness = -1)
        # cv2.putText(frame, text, (det[0], det[1]-5), cv2.FONT_HERSHEY_SIMPLEX, text_scale, color, 1)
        draw_text(frame, text, (det[0], det[1]-5), cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0,0,0), 1, color)
        return frame, status
    else:
        return frame, status

def draw_info(frame, latency, count1,count2):
    # cv2.putText(frame, 'Latency {}ms'.format(round(latency*(10**3),2)), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (163,3,27), 2)
    # cv2.putText(frame, 'Count {}'.format(count), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (163,3,27), 2)
    text_w1, _ = draw_text(frame, 'Illegal Parking {}'.format(count1), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, (0,0,0))
    text_w2, _ = draw_text(frame, 'Improper Lane Usage {}'.format(count2), (20+text_w1,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, (0,0,0))
    draw_text(frame, 'Latency {}ms'.format(round(latency*(10**3),2)), (30+text_w2+text_w1,10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2, (0,0,0))
    return frame 

def draw_lanes(frame,Rlinelist,Midlinelist,Llinelist,W,H):
    if min(W,H)>160: 
        r = int(min(H,W)/160)
    else:
        r = 1
    cv2.circle(frame, Rlinelist[0] ,radius= r, color = (255, 0, 0),thickness = -1)
    cv2.circle(frame, Midlinelist[0] ,radius= r, color = (255, 0, 0),thickness = -1)
    cv2.circle(frame, Llinelist[0] ,radius= r, color = (255, 0, 0),thickness = -1)
    for i in range(len(Rlinelist)-1):
        cv2.circle(frame, Rlinelist[i+1] ,radius= r, color = (255, 0, 0),thickness = -1)
        cv2.line(frame,Rlinelist[i],Rlinelist[i+1],(255,0,0),1)
    for i in range(len(Midlinelist)-1):
        cv2.circle(frame, Midlinelist[i+1] ,radius= r, color = (255, 0, 0),thickness = -1)
        cv2.line(frame,Midlinelist[i],Midlinelist[i+1],(255,0,0),1)
    for i in range(len(Llinelist)-1):
        cv2.circle(frame, Llinelist[i+1] ,radius= r, color = (255, 0, 0),thickness = -1)
        cv2.line(frame,Llinelist[i],Llinelist[i+1],(255,0,0),1)

    alpha = 0.15
    int_coords = lambda x: np.array(x).round().astype(np.int32)
    exteriorR = [int_coords(config.polygonR.exterior.coords)]
    exteriorL = [int_coords(config.polygonL.exterior.coords)]

    overlayR = frame.copy()
    cv2.fillPoly(overlayR, exteriorR, color = (255, 81, 31))
    cv2.addWeighted(overlayR, alpha, frame, 1 - alpha, 0, frame)

    overlayL = frame.copy()
    cv2.fillPoly(overlayL, exteriorL, color = (39, 237, 250))
    cv2.addWeighted(overlayL, alpha, frame, 1 - alpha, 0, frame)

    return frame

def draw_text(img, text,
          pos=(0, 0),
          font=cv2.FONT_HERSHEY_PLAIN,
          font_scale=3,
          text_color=(0, 255, 0),
          font_thickness=2,
          text_color_bg=(0, 0, 0)
          ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, int(y + text_h + font_scale - 1)), font, font_scale, text_color, font_thickness)
    return text_w, text_h

def mouse_handler(event, x, y, flags, data):
    global btn_down
    global ix
    global iy
    if min(data['w'],data['h'])>160: 
        r = int(min(data['w'],data['h'])/160)
    else:
        r = 1

    if event == cv2.EVENT_LBUTTONUP and btn_down:
        #if you release the button, finish the line
        btn_down = False
        data['points'].append((ix, iy)) #append the point
        cv2.circle(data['im'], (ix, iy) ,radius= r, color = (0, 0, 255),thickness = -1)
        cv2.circle(data['imtext'], (ix, iy) ,radius= r, color = (0, 0, 255),thickness = -1)
        cv2.imshow("Image", data['imtext'])

    elif event == cv2.EVENT_LBUTTONDOWN :
        btn_down = True
        ix , iy = x , y

def get_points(im,imtext,w,h):
    # Set up data to send to mouse handler
    data = {}
    data['im'] = im
    data['imtext'] = imtext
    data['points'] = []
    data['w'] = w
    data['h'] = h

    # Set the callback function for any mouse event
    cv2.imshow("Image", imtext)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)

    # Convert array to np.array in shape n,2,2
    points = data['points']

    return points, data['im']

if __name__ == "__main__":

    inputfile = r'C:\Users\thara\Desktop\Vehicle_videos\vehicle1.mp4' 
    vs = cv2.VideoCapture(inputfile)
    (W, H) = (int(vs.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    (grabbed, frame) = vs.read()
    if grabbed:
        pts, final_image = get_points(frame,W,H)
        print('Width:',W)
        print('Height:',H)
        print (pts)