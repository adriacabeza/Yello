import datetime
import time
import sys
import os
import tellopy
import cv2
import av
from pynput import keyboard
from darkflow.net.build import TFNet
import numpy as np

from ctypes import *
from subprocess import Popen, PIPE

MODEL_PATH = 'cfg/yolov2-tiny-voc.cfg'
WEIGHTS_PATH = 'cfg/yolov2-tiny-voc.weights'
MODEL_THRESHOLD = 0.35


video_player = None
video_recorder = None
keydown = None
date_fmt = '%Y-%m-%d_%H%M%S'
filename= None
recording = None

# creating object Drone
drone = tellopy.Tello()
drone.connect()


def toggle_recording():
    global video_recorder
    global date_fmt
    global filename
    global recording
    if filename != None:
        recording = False
        filename = None
    # start a new recording
    else:
        filename = '%s/Pictures/tello-%s.mp4' % (
            os.getenv('HOME'), datetime.datetime.now().strftime(date_fmt))
        print('Recording video to %s' % filename)



def handleFileReceived(event, sender, data):
    global date_fmt
    # Create a file in ~/Pictures/ to receive image data from the drone.
    path = '%s/Pictures/tello-%s.jpeg' % (
        os.getenv('HOME'),
        datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    with open(path, 'wb') as fd:
        fd.write(data)
    print('Saved photo to %s' % path)



net = TFNet({
    'model': MODEL_PATH,
    'load': WEIGHTS_PATH,
    'threshold': MODEL_THRESHOLD
})

controls = {
    'w': lambda: drone.forward(5),
    'a': lambda: drone.left(5),
    's': lambda:  drone.backward(5),
    'd': lambda: drone.right(5),
    'i': lambda: drone.flip_forward(),
    'k': lambda: drone.flip_back(),
    'j': lambda: drone.flip_left(),
    'l': lambda: drone.flip_right(),
    'Key.left': lambda : drone.counter_clockwise(50 * 2),
    'Key.right': lambda : drone.clockwise(50 * 2),
    'Key.up': lambda : drone.up(80 * 2),
    'Key.down': lambda : drone.down(80 * 2),
    'Key.tab': lambda: drone.takeoff(),
    'Key.backspace': lambda: drone.land(),
    'p': lambda: drone.palm_land(),
    'Key.enter': lambda: drone.take_picture(),
    'v': lambda: toggle_recording(),
    'c': lambda: drone.clockwise_degrees(360),
}


def on_press(keyname):
    global keydown
    if keydown:
        return
    try:
        keydown = True
        keyname = str(keyname).strip('\'')
        print('+' + keyname)
        if keyname == 'Key.esc':
            drone.quit()
            exit(0)
        if keyname in controls:
            controls[keyname]()
    except AttributeError:
        print('special key {0} pressed'.format(keyname))


def on_release(keyname):
    keydown = False
    keyname = str(keyname).strip('\'')
    print('-' + keyname)
    if keyname in controls:
        controls[keyname]()


def video():
    global filename
    global recording
    key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    key_listener.start()
    colors = [tuple(255 * np.random.rand(3)) for _ in range(20)]
    retry = 3
    container = None
    while container is None and 0 < retry:
            retry -= 1
            try:
                    container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                    print(ave)
                    print('Retry...')

    # skip first 300 frames
    frame_skip = 300
    while True:
        for frame in container.decode(video=0):
                if filename != None and not recording:
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        video_writer = cv2.VideoWriter(filename, fourcc, 20, (680, 480))
                        recording = True
                if 0 < frame_skip:
                        frame_skip = frame_skip - 1
                        continue
                if frame.time_base < 1.0/60:
                        time_base = 1.0/60
                else:
                        time_base = frame.time_base

                # Convert frame to cv2 image
                frame = cv2.cvtColor(
                        np.array(frame.to_image(), dtype=np.uint8), cv2.COLOR_RGB2BGR)
                frame = cv2.resize(frame, (640, 480))
                start_time = time.time()
                results = net.return_predict(frame)
                for color, result in zip(colors, results):
                        tl = (result['topleft']['x'], result['topleft']['y'])
                        br = (result['bottomright']['x'],
                                        result['bottomright']['y'])
                        label = result['label']
                        confidence = result['confidence']
                        text = '{}: {:.0f}%'.format(label, confidence * 100)
                        frame = cv2.rectangle(frame, tl, br, color, 5)
                        frame = cv2.putText(
                                frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
                cv2.imshow('frame', frame)
                if filename != None and recording:
                    video_writer.write(frame)
                print('FPS {:.1f}'.format(1 / (time.time() - start_time)))
                cv2.waitKey(1)
                frame_skip = int((time.time() - start_time)/time_base)
    print('Shutting down connection to drone...')
    drone.quit()
    cv2.destroyAllWindows()


drone.subscribe(drone.EVENT_FILE_RECEIVED, handleFileReceived)

if __name__ == '__main__':
    video()
