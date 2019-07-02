import datetime
from subprocess import Popen, PIPE
import time
import struct
import sys
import os
import tellopy
import cv2.cv2 as cv2  
import av
import argparse
import traceback
from pynput import keyboard
from ctypes import *
import numpy as np


parser = argparse.ArgumentParser(description='Insert parameters for Yello')
parser.add_argument('--library','--l', type=str, help = 'Insert the library path of libdarknet.so', default= "/root/darknet/libdarknet.so")
parser.add_argument('--config','--g', type=str, help= 'Insert the cfg file path of the model', default="/root/darknet/cfg/yolov3-tiny.cfg")
parser.add_argument('--data', '--d', type=str, help= 'Insert the data file path of the model', default="/root/Yello/tiny.data")
parser.add_argument('--weights', '--w', type=str, help= 'Insert the weight file path of the model', default="/root/darknet/yolov3-tiny.weights")
args = parser.parse_args()


drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(30.0)
drone.subscribe(drone.EVENT_FLIGHT_DATA, flight_data_handler)
drone.subscribe(drone.EVENT_FILE_RECEIVED, handle_flight_received)

prev_flight_data = None
video_player = None
video_recorder = None
font = None
keydown = None
wid = None
speed = 50
date_fmt = '%Y-%m-%d_%H%M%S'

def toggle_recording(drone, speed):
    global video_recorder
    global date_fmt
    if speed == 0:
        return

    if video_recorder:
        # already recording, so stop
        video_recorder.stdin.close()
        print('Video saved to %s' % video_recorder.video_filename)
        video_recorder = None
        return

    # start a new recording
    filename = '%s/Pictures/tello-%s.mp4' % (os.getenv('HOME'),
                                             datetime.datetime.now().strftime(date_fmt))
    video_recorder = Popen([
        'mencoder', '-', '-vc', 'x264', '-fps', '30', '-ovc', 'copy',
        '-of', 'lavf', '-lavfopts', 'format=mp4',
        # '-ffourcc', 'avc1',
        # '-really-quiet',
        '-o', filename,
    ], stdin=PIPE)
    video_recorder.video_filename = filename
    print('Recording video to %s' % filename)

def take_picture(drone, speed):
    if speed == 0:
        return
    drone.take_picture()

def palm_land(drone, speed):
    if speed == 0:
        return
    drone.palm_land()

controls = {
    'w': 'forward',
    's': 'backward',
    'a': 'left',
    'd': 'right',
    'space': 'up',
    'left shift': 'down',
    'right shift': 'down',
    'q': 'counter_clockwise',
    'e': 'clockwise',
    'i': lambda speed: self.drone.flip_forward(),
    'k': lambda speed: self.drone.flip_back(),
    'j': lambda speed: self.drone.flip_left(),
    'l': lambda speed: self.drone.flip_right(),
    'left': lambda drone, speed: drone.counter_clockwise(speed*2),
    'right': lambda drone, speed: drone.clockwise(speed*2),
    'up': lambda drone, speed: drone.up(speed*2),
    'down': lambda drone, speed: drone.down(speed*2),
    'tab': lambda drone, speed: drone.takeoff(),
    'backspace': lambda drone, speed: drone.land(),
    'p': palm_land,
    'r': toggle_recording,
    'z': toggle_zoom,
    'enter': take_picture,
    'return': take_picture
}


class FlightDataDisplay(object):
    _value = None
    _surface = None
    _update = None
    def __init__(self, key, format, colour=(255,255,255), update=None):
        self._key = key
        self._format = format
        self._colour = colour

        if update:
            self._update = update
        else:
            self._update = lambda drone,data: getattr(data, self._key)

    def update(self, drone, data):
        new_value = self._update(drone, data)
        if self._value != new_value:
            self._value = new_value
            self._surface = font.render(self._format % (new_value,), True, self._colour)
        return self._surface

def update_hud(hud, drone, flight_data):
    (w,h) = (158,0) # width available on side of screen in 4:3 mode
    blits = []
    for element in hud:
        surface = element.update(drone, flight_data)
        if surface is None:
            continue
        blits += [(surface, (0, h))]
        # w = max(w, surface.get_width())
        h += surface.get_height()
    h += 64  # add some padding
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0,0,0)) # remove for mplayer overlay mode
    for blit in blits:
        overlay.blit(*blit)
    pygame.display.get_surface().blit(overlay, (0,0))
    pygame.display.update(overlay.get_rect())


hud = [
    FlightDataDisplay('height', 'ALT %3d'),
    FlightDataDisplay('ground_speed', 'SPD %3d'),
    FlightDataDisplay('battery_percentage', 'BAT %3d%%'),
    FlightDataDisplay('wifi_strength', 'NET %3d%%'),
    FlightDataDisplay(None, 'CAM %s', update=flight_data_mode),
    FlightDataDisplay(None, '%s', colour=(255, 0, 0), update=flight_data_recording),
]

key_listener = keyboard.Listener(on_press=on_press,on_release=on_release)
key_listener.start()

def on_press(keyname):
    if self.keydown:
            return
        try:
            keydown = True
            keyname = str(keyname).strip('\'')
            print('+' + keyname)
            if keyname == 'Key.esc':
                drone.quit()
                exit(0)
            if keyname in controls:
                key_handler = controls[keyname]
                if isinstance(key_handler, str):
                    getattr(drone, key_handler)(speed)
                else:
                    key_handler(speed)
        except AttributeError:
            print('special key {0} pressed'.format(keyname))

def on_release(keyname):
        keydown = False
        keyname = str(keyname).strip('\'')
        print('-' + keyname)
        if keyname in controls:
            key_handler = controls[keyname]
            if isinstance(key_handler, str):
                getattr(drone, key_handler)(0)
            else:
                key_handler(0)

def flightDataHandler(event, sender, data):
    global prev_flight_data
    text = str(data)
    if prev_flight_data != text:
        update_hud(hud, sender, data)
        prev_flight_data = text


def handleFileReceived(event, sender, data):
    global date_fmt
    # Create a file in ~/Pictures/ to receive image data from the drone.
    path = '%s/Pictures/tello-%s.jpeg' % (
        os.getenv('HOME'),
        datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    with open(path, 'wb') as fd:
        fd.write(data)
    print('Saved photo to %s' % path)



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
    


lib = CDLL(args.library,RTLD_GLOBAL)
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

net = load_net(args.config.encode(),args.weights.encode(), 0)
meta = load_meta(args.data.encode())

#TODO: control drone with hands. Example: red for palmup --> stop, green for thumbsup --> go
classes_box_colors = [(0, 0, 255), (0, 255, 0)]
classes_font_colors = [(255, 255, 0), (0, 255, 255)]

def array_to_image(arr):
    # need to return old values to avoid python freeing memory
    arr = arr.transpose(2,0,1)
    c, h, w = arr.shape[0:3]
    arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
    data = arr.ctypes.data_as(POINTER(c_float))
    im = IMAGE(w,h,c,data)
    return im,arr


def video():
    nms = .45
    thresh=.5
    hier_thresh=.3
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
            time.sleep(0.3)
            for i,frame in enumerate(container.decode(video=0)):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                try:
                    start_time = time.time()
                    im, array = array_to_image(np.array(frame.to_image()))
                    image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
                    
                    num = c_int(0)
                    if i % 3 == 0:
                        pnum = pointer(num)
                        predict_image(net, im)
                        dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
                        num = pnum[0]
                        if (nms): do_nms_obj(dets, num, meta.classes, nms);
                        # res = []
                        print("\n\n\n\nFounded {} objects: {} \n\n\n".format(len(num), ", ".join(num)))
                        for j in range(num):
                            print('Debug0')
                            for i in range(meta.classes):
                                print('Debug1')
                                if dets[j].prob[i] > 0:
                                    b = dets[j].bbox
                                    x1 = int(b.x - b.w / 2.)
                                    y1 = int(b.y - b.h / 2.)
                                    x2 = int(b.x + b.w / 2.)
                                    y2 = int(b.y + b.h / 2.)
                                    print((x1,y1),(x2,y2))
                                    cv2.rectangle(array, (x1, y1), (x2, y2), classes_box_colors[i], 2)
                                    cv2.puttext(array, meta.names[i], (x1, y1 - 20), 1, 1, classes_font_colors[i], 2, cv2.line_aa)
                                    print('Detected: {}'.format(meta.names[i]))
                    cv2.imshow('Original', image) 
                    cv2.imshow('Output', array)
                    cv2.waitKey(1)
                    if frame.time_base < 1.0/60:
                        time_base = 1.0/60
                    else:
                        time_base = frame.time_base
                    frame_skip = int((time.time() - start_time)/time_base)
                except Exception as exp:
                    print(exp)

            if cv2.waitKey(1) == ord('q'):
                break        

    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        print('Shutting down connection to drone...')
        drone.quit()
        cv2.destroyAllWindows()



def main():
   video()


if __name__ == '__main__':
    main()
