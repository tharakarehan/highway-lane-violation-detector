import numpy as np
import cv2
import time
import logging as log
import sys
from openvino.inference_engine import IECore

class vehicleDetector():

    def __init__(self, path, height, width, threshold):

        self.w = width
        self.h = height
        self.path = path
        self.threshold = threshold
    
    def load(self):

        log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
        log.info("Loading Inference Engine")
        ie = IECore()

        log.info(f"Loading network:\n\t{self.path}")
        self.net = ie.read_network(model=self.path)
        self.input_key = next(iter(self.net.input_info.keys()))
        log.info("Device info:")
        versions = ie.get_versions("CPU")
        print("{}{}".format(" " * 8, "CPU"))
        print("{}MKLDNNPlugin version ......... {}.{}".format(" " * 8, versions["CPU"].major,
                                                            versions["CPU"].minor))
        print("{}Build ........... {}".format(" " * 8, versions["CPU"].build_number))
        
        print("input shape: " + str(self.net.input_info[self.input_key].input_data.shape))

        self.n, self.c, self.ih, self.iw = self.net.input_info[self.input_key].input_data.shape

        self.out_blob = next(iter(self.net.outputs))

        self.net.input_info[self.input_key].precision = 'U8'

        self.exec_net = ie.load_network(network = self.net, device_name="CPU")

    def preprocess(self,image):

        images = np.ndarray(shape=(1, self.c, self.ih, self.iw))
        if (self.ih, self.iw) != (self.h, self.w):
            image = cv2.resize(image, (self.iw, self.ih))
        image = image.transpose((2, 0, 1))  
        images[0] = image
        return images
        
    def predict(self, image):

        data = {}
        images = self.preprocess(image)
        data[self.input_key] = images
        res = self.exec_net.infer(inputs=data)
        dets = self.postprocess(res)
        return dets

    def postprocess(self, res):
        res = res[self.out_blob]
        dets = []
        data = res[0][0]
        for number, proposal in enumerate(data):
            if proposal[2] > self.threshold:
                xmin = np.int(self.w * proposal[3])
                ymin = np.int(self.h * proposal[4])
                xmax = np.int(self.w * proposal[5])
                ymax = np.int(self.h * proposal[6])
                
                dets.append([xmin, ymin, xmax, ymax, 1])
        
        dets = np.array(dets)
        return dets
                

