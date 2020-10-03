# Yello (Yolo + DJI Tello)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/adriacabeza/Yello/pulls)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/adriacabeza/Yello)

<p align="center">
	<img src="./images/logo.png"></img>
</p>

This repository contains a project that combines DJI Tello and Deep Learning (Tiny Yolo). The aim of this project is to detect several objects using the drone. It uses [Darkflow](https://github.com/thtrieu/darkflow): an open source project that translates darknet to tensorflow) and [TelloPy](https://github.com/hanyazou/TelloPy) : a super friendly api for the drone. **Still under construction**

## TODO
- Test it (my drone is in Barcelona and I am in quarantine).
- Set actions when something is detected i.e. take a photo when a person is detected.
- Organize it

# Installation

1. Setup environment
2. Install dependencies
```bash 
$ pip3 install -r requirements.lock
```
3. Install [Darkflow](https://github.com/thtrieu/darkflow.git)
4. Install configuration files and weights
```bash
$ mkdir cfg
$ cd cfg
$ wget https://pjreddie.com/media/files/yolov2-tiny-voc.weights
$ wget https://github.com/pjreddie/darknet/blob/master/cfg/yolov2-tiny-voc.cfg
```

## Demo video with Tiny-Yolo

If you want to run Yello and see how it works, you can run it by typing:

```bash
$ python -m src --model yolov2-tiny-voc 
```
Then, after setting a connection to the drone and preparing the video stream, two windows will show up, the original and the one with predictions. 

![](images/predictions.jpg)

#### Controls

```python
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
```

## Additional information about the drone

- **Tello communication protocol** = UDP
- **Tello IP** = 192.168.10.1
- **Tello Port for commands** = 8899
- **Tello Port for video** = 6038
- **Lights**:
	- Flashing blue: charging 
	- Solid blue: charged
	- Flashing purple: booting up
	- Flashing yellow fast: wifi network, waiting for connection 
	- Flashing yellow: user connected 

## Execute orders to the drone
> For more information check [TelloPy](https://github.com/hanyazou/TelloPy/tree/develop-0.7.0/tellopy/_internal), to execute orderts to the drone, you have to send packets with the hex code of the instruction that is desired. Here we can find some examples:

| Code   | Instruction |
|--------|-------------|
| 0x0054 | Take off    |
| 0x0055 | Land        |
| 0x005e | Palm Land   |
| 0x0030 | Take Picture|
| 0x005d | Throw & Go  |


Or use the Tellopy API and call a method that does it for you. Let's see some examples with both options (if you want to run them you can find them in commands_test.py):

**Sending the packet**

```python
drone = tellopy.Tello()
protcol = tellopy._internal.protocol()
drone.connect()
drone.wait_for_connection(60.0)

# take_off
pkt = protocol.Packet(0x0054)
pkt.fixup()
drone.send_packet(pkt)
sleep(2)

# flip to the right, if you have less than 60% of battery comment all the lines until land
pkt = protocol.Packet(0x005c, 0x70)
pkt.add_byte(4)
pkt.fixup()
drone.send_packet(pkt)
sleep(2)

# land
pkt = protocol.Packet(0x0055)
pkt.add_byte(0x00)
pkt.fixup()
drone.send_packet(pkt)

```


**Calling the API**

```python
drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(60.0)
drone.take_off()
sleep(2)

# flip to the right, if you have less than 60% of battery comment lines until drone.land()
drone.flip_forwardright()
sleep(2)

drone.land()
```

However it really depends on what you want to do since there are several different structures of packets. If you want to know more about how it works check the source code of the API. 


