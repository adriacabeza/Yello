import datetime
import time
import sys
import pygame
import os
import tellopy
import cv2
import av
import argparse
import traceback

import numpy as np

from src import *
from ctypes import *
from subprocess import Popen, PIPE


prev_flight_data = None
video_player = None
video_recorder = None
font = None
keydown = None
wid = None
speed = 50
date_fmt = '%Y-%m-%d_%H%M%S'

# creating object Drone
drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(10.0)


def handler(event, sender, data):
	global flight_data
	drone = sender
	if event is drone.EVENT_FLIGHT_DATA:
		flight_data = data
		print(flight_data)


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
	filename = '%s/Pictures/tello-%s.mp4' % (os.getenv('HOME'), datetime.datetime.now().strftime(date_fmt))
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
	'i': lambda speed: drone.flip_forward(),
	'k': lambda speed: drone.flip_back(),
	'j': lambda speed: drone.flip_left(),
	'l': lambda speed: drone.flip_right(),
	'left': lambda drone, speed: drone.counter_clockwise(speed * 2),
	'right': lambda drone, speed: drone.clockwise(speed * 2),
	'up': lambda drone, speed: drone.up(speed * 2),
	'down': lambda drone, speed: drone.down(speed * 2),
	'tab': lambda drone, speed: drone.takeoff(),
	'backspace': lambda drone, speed: drone.land(),
	'p': palm_land,
	'r': toggle_recording,
}


class FlightDataDisplay(object):
	_value = None
	_surface = None
	_update = None

	def __init__(self, key, format, colour=(255, 255, 255), update=None):
		self._key = key
		self._format = format
		self._colour = colour

		if update:
			self._update = update
		else:
			self._update = lambda drone, data: getattr(data, self._key)

	def update(self, drone, data):
		new_value = self._update(drone, data)
		if self._value != new_value:
			self._value = new_value
			self._surface = font.render(self._format % (new_value,), True, self._colour)
		return self._surface


def update_hud(hud, drone, flight_data):
	(w, h) = (158, 0)  # width available on side of screen in 4:3 mode
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
	overlay.fill((0, 0, 0))  # remove for mplayer overlay mode
	for blit in blits:
		overlay.blit(*blit)
	pygame.display.get_surface().blit(overlay, (0, 0))
	pygame.display.update(overlay.get_rect())


def on_press(keyname):
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


hud = [
	FlightDataDisplay('height', 'ALT %3d'),
	FlightDataDisplay('ground_speed', 'SPD %3d'),
	FlightDataDisplay('battery_percentage', 'BAT %3d%%'),
	FlightDataDisplay('wifi_strength', 'NET %3d%%'),
]


def video():
	net = TFNET({
		'model': MODEL_PATH
		'load': WEIGHTS_PATH
		'threshold': MODEL_THRESHOLD
	})
	
	global flight_data
	colors = [tuple(255* np.random.rand(3)) for _ in range(10)]
	try:
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
				try:
					start_time = time.time()
					cv2.imshow("org", frame)
					results = net.return_predict(frame)
					print("\nFounded {} objects\n".format(results))
					for color, result in zip(colors, results):
						tl = (result['topleft']['x'], result['topleft']['y'])
                				br = (result['bottomright']['x'], result['bottomright']['y'])
				                label = result['label']
				                confidence = result['confidence']
				                text = '{}: {:.0f}%'.format(label, confidence * 100)
				                frame = cv2.rectangle(frame, tl, br, color, 5)
				                frame = cv2.putText(frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
           				cv2.imshow('frame', frame)
           				print('FPS {:.1f}'.format(1 / (time.time() - start_time)))							
					# uploading frame rate
					if frame.time_base < 1.0 / 20:
						time_base = 1.0 / 20
					else:
						time_base = frame.time_base
					frame_skip = int((time.time() - start_time) / time_base)
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


if __name__ == '__main__':
	video()
