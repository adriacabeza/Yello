import datetime
import time
import sys
import os
import tellopy
import cv2
import av
# import argparse
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

# creating object Drone
drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(2.0)


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
    filename = '%s/Pictures/tello-%s.mp4' % (
        os.getenv('HOME'), datetime.datetime.now().strftime(date_fmt))
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
    'i': lambda speed: drone.flip_forward(),
    'k': lambda speed: drone.flip_back(),
    'j': lambda speed: drone.flip_left(),
    'l': lambda speed: drone.flip_right(),
    'Key.left': lambda : drone.counter_clockwise(50 * 2),
    'Key.right': lambda : drone.clockwise(50 * 2),
    'Key.up': lambda : drone.up(80 * 2),
    'Key.down': lambda : drone.down(80 * 2),
    'Key.tab': lambda: drone.takeoff(),
    'Key.enter': lambda: drone.land(),
    'p': lambda: drone.palm_land(),
    'c': lambda: take_picture(),
    'r': lambda: toggle_recording(),
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
        key_handler = controls[keyname]
        if isinstance(key_handler, str):
            getattr(drone, key_handler)(0)
        else:
            key_handler(0)


def video():
    net = TFNet({
        'model': MODEL_PATH,
        'load': WEIGHTS_PATH,
        'threshold': MODEL_THRESHOLD
    })
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
                    #print("\nFound {} objects\n".format(len(results)))
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
                    #print('FPS {:.1f}'.format(1 / (time.time() - start_time)))
                    cv2.waitKey(1)
                    frame_skip = int((time.time() - start_time)/time_base)
    print('Shutting down connection to drone...')
    drone.quit()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    video()
