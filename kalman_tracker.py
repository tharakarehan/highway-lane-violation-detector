import numpy as np
from filterpy.kalman import KalmanFilter
import statistics

class KalmanBoxTracker(object):
    """
    This class represents the internal state of individual tracked objects observed as bbox.
    """
    count = 0
    def __init__(self, bbox, length, stdvar,img=None):
        """
        Initialises a tracker using initial bounding box.
        """
        # Define constant velocity model
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([[1,0,0,0,1,0,0],[0,1,0,0,0,1,0],[0,0,1,0,0,0,1],[0,0,0,1,0,0,0],  [0,0,0,0,1,0,0],[0,0,0,0,0,1,0],[0,0,0,0,0,0,1]])
        self.kf.H = np.array([[1,0,0,0,0,0,0],[0,1,0,0,0,0,0],[0,0,1,0,0,0,0],[0,0,0,1,0,0,0]])

        self.kf.R[2:, 2:] *= 10.
        self.kf.P[4:, 4:] *= 1000. 
        self.kf.P *= 10.
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01

        self.kf.x[:4] = convert_bbox_to_z(bbox)
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
        self.xlist = []
        self.ylist = []
        self.length = length
        self.dynamicstste = 1
        self.stdvar = stdvar

    def update(self, bbox, img=None):
        """
        Updates the state vector with observed bbox.
        """
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1

        if len(bbox) != 0:
            self.kf.update(convert_bbox_to_z(bbox))

    def predict(self,img=None):
        """
        Advances the state vector and returns the predicted bounding box estimate.
        """
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0

        self.kf.predict()
        self.age += 1

        if self.time_since_update > 0:
            self.hit_streak = 0

        self.time_since_update += 1
        self.history.append(convert_x_to_bbox(self.kf.x))

        return self.history[-1][0]

    def get_state(self):
        """
        Returns the current bounding box estimate and dynamic state.
        """
        zbox = self.kf.x
        # print(zbox)
        if len(self.xlist) >= self.length:
            self.xlist.pop(0)
            self.xlist.append(zbox[0][0])
        else:
            self.xlist.append(zbox[0][0])
        
        if len(self.ylist) >= self.length:
            self.ylist.pop(0)
            self.ylist.append(zbox[1][0])
        else:
            self.ylist.append(zbox[1][0])

        if len(self.xlist) > 1:
            # print(self.xlist)
            xstd = statistics.stdev(self.xlist)
            ystd = statistics.stdev(self.ylist)

            if xstd < self.stdvar and ystd < self.stdvar and len(self.xlist) >= self.length :
                self.dynamicstste = 0
            else:
                self.dynamicstste = 1

        return np.concatenate((convert_x_to_bbox(zbox)[0],[self.dynamicstste]))


def convert_bbox_to_z(bbox):
    """
    Takes a bounding box in the form [x1,y1,x2,y2] and returns z in the form
    [x,y,s,r] where x,y is the centre of the box and s is the scale/area and r is
    the aspect ratio
    """
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = bbox[0] + w/2.
    y = bbox[1] + h/2.
    s = w * h 
    r = w / float(h)
    return np.array([x, y, s, r]).reshape((4, 1))

def convert_x_to_bbox(x,score=None):
    """
    Takes a bounding box in the centre form [x,y,s,r] and returns it in the form
    [x1,y1,x2,y2] where x1,y1 is the top left and x2,y2 is the bottom right
    """
    w = np.sqrt(x[2] * x[3])
    h = x[2] / w

    if score == None:
        return np.array([x[0]-w/2., x[1]-h/2., x[0]+w/2., x[1]+h/2.]).reshape((1, 4))
    else:
        return np.array([x[0]-w/2., x[1]-h/2., x[0]+w/2., x[1]+h/2., score]).reshape((1, 5))



