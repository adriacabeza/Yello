import datetime
from subprocess import Popen, PIPE
import threading
import socket
import time
import struct
import sys
import os
from . protocol import *
import tellopy
import cv2.cv2 as cv2  
import av
import traceback

from ctypes import *
import numpy

drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(60.0)

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]
    


lib = CDLL("/home/adria/Documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int
load_net = lib.load_network

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

net = load_net(b"/home/adria/Documents/darknet/cfg/yolov3-tiny.cfg", b"/home/adria/Documents/darknet/yolov3-tiny.weights", 0)
meta = load_meta(b"/home/adria/Documents/darknet/data/coco.names")


def commands():
    pkt = Packet(0x0054)
    pkt.fixup()
    drone.send_packet(pkt)
    # drone.takeoff()

    time.sleep(2)
    print("2 secs")


    # drone.flip_forwardright()
    pkt = Packet(0x005c, 0x70)
    pkt.add_byte(4)
    pkt.fixup()
    drone.send_packet(pkt)


    time.sleep(4)
    print("4 secs")
    # drone.land()

    pkt = Packet(0x0055)
    pkt.add_byte(0x00)
    pkt.fixup()
    drone.send_packet(pkt)


def array_to_image(arr):
    # need to return old values to avoid python freeing memory
    arr = arr.transpose(2,0,1)
    c, h, w = arr.shape[0:3]
    arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
    data = arr.ctypes.data_as(POINTER(c_float))
    im = IMAGE(w,h,c,data)
    return im, arr


def video():
    try:
        retry = 3
        container = None
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        # skip first 300 frames
        frame_skip = 300
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()
                image = frame.to_image()

                im, image = array_to_image(image)
                rgbgr_image(im)
                num = c_int(0)
                pnum = pointer(num)
                predict_image(net, im)
                dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
                num = pnum[0]
                if (nms): do_nms_obj(dets, num, meta.classes, nms);
                # res = []
                for j in range(num):
                    for i in range(meta.classes):
                        if dets[j].prob[i] > 0:
                            b = dets[j].bbox
                            x1 = int(b.x - b.w / 2.)
                            y1 = int(b.y - b.h / 2.)
                            x2 = int(b.x + b.w / 2.)
                            y2 = int(b.y + b.h / 2.)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), classes_box_colors[i], 2)
                            cv2.putText(frame, meta.names[i], (x1, y1 - 20), 1, 1, classes_font_colors[i], 2, cv2.LINE_AA)
                                    
                cv2.imshow('output', frame)

                
                
                cv2.imshow('Original', image)
                cv2.waitKey(1)
                if frame.time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame.time_base
                frame_skip = int((time.time() - start_time)/time_base)
                    

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()



def main():
    # commands()
    video()


if __name__ == '__main__':
    main()