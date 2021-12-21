import config
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from utils import image_utils
import cv2
import numpy as np

def compare_pos(det,width,height):
   
    if (abs(det[2] - det[0]) > 0.04 * width) and (abs(det[3] - det[1]) > 0.04 * height):
        x, y = int((det[0]+det[2])/2),int((det[1]+det[3])/2)
        point = Point(x, y)
        if config.polygonR.contains(point):
            return 'R'
        elif config.polygonL.contains(point):
            return 'L'
        else:
            return 'N'
    else:
        return 'N'

if __name__ == '__main__':
    inputfile = r'C:\Users\thara\Desktop\Vehicle_videos\vehicle1.mp4' 
    vs = cv2.VideoCapture(inputfile)
    (W, H) = (int(vs.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT)))
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

            # cods , _ = image_utils.get_points(left_image,left_image,W,H)
            # cv2.imshow("Image", left_image)
            # cv2.waitKey(0)
            cv2.destroyAllWindows()

            polygonR = Polygon(config.right_pts + config.middle_pts[ : :-1])
            polygonL = Polygon(config.left_pts + config.middle_pts[: :-1])
            # x,y = cods[0]
            # point = Point(x, y)
            # print('X',x,'Y',y)
            # print('Right',polygonR.contains(point))
            # print('Left',polygonL.contains(point))

            alpha = 0.15
            int_coords = lambda x: np.array(x).round().astype(np.int32)
            exteriorR = [int_coords(polygonR.exterior.coords)]
            exteriorL = [int_coords(polygonL.exterior.coords)]

            overlayR = left_image.copy()
            cv2.fillPoly(overlayR, exteriorR, color = (255, 81, 31))
            cv2.addWeighted(overlayR, alpha, left_image, 1 - alpha, 0, left_image)

            overlayL = left_image.copy()
            cv2.fillPoly(overlayL, exteriorL, color = (39, 237, 250))
            cv2.addWeighted(overlayL, alpha, left_image, 1 - alpha, 0, left_image)

            cv2.imshow("Polygon", left_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()