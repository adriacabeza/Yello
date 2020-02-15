# Yello (Yolo + DJI Tello)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/adriacabeza/Yello/pulls)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/adriacabeza/Yello)

<p align="center">
	<img src="./logo.png"></img>
</p>
This repository contains a project that combines DJI Tello and Deep Learning (Tiny Yolo). The aim of this project is to   detect several objects using the drone. It uses [Darknet](https://github.com/pjreddie/darknet): an open source neural network framework written in C and CUDA) and [TelloPy](https://github.com/hanyazou/TelloPy) : a super friendly api for the drone. 

Although  the weights of the model can be changed, I used the ones pretrained from the official website ([YOLOv3- tiny](https://pjreddie.com/media/files/yolov3-tiny.weights)). 

# Installation

Moreover, you can add functionalities easily in the project. Already implemented functionalities:
- https://www.youtube.com/watch?v=lcFNaKYZzaE&list=LL2s_aH9Icya9ej3nQZ_9TtQ&index=4&t=3647s

## Demo video with Tiny-Yolo

If you want to run Yello and see how it works, you can run it by typing:

```bash
STILL NOT WORKING
# cd Yello
# python yello.py 

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
> for more information check [TelloPy](https://github.com/hanyazou/TelloPy/tree/develop-0.7.0/tellopy/_internal)
To execute orderts to the drone, you have to send packets with the hex code of the instruction that is desired. Here we can find some examples:

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

# flip to the right, if you have less than 60% of battery comment lines until land
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

## YELLO USING DOCKER

First you have to clone the repository. 
To continue you need to have docker installed (follow the instructions here https://docs.docker.com/install/). Then, to build the docker write in the repository folder: 
``` 
docker build --no-cache -t yello .
```
> NOTE: It can last several minutes to finish building.
Then, after setting the DISPLAY environment variable and lettig docker use it, you will be able to do run the docker:

```
export DISPLAY=":0.0" 
xhost + 
docker run -ti --rm -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix yello bash

```

To test if everything went correct, you can run a test with tiny-yolo:
````
# cd darknet 
#./darknet detector test cfg/coco.data cfg/yolov3-tiny.cfg /root/yolov3-tiny.weights data/dog.jpg
layer     filters    size              input                output
    0 conv     32  3 x 3 / 1   416 x 416 x   3   ->   416 x 416 x  32
    1 max          2 x 2 / 2   416 x 416 x  32   ->   208 x 208 x  32
    2 conv     64  3 x 3 / 1   208 x 208 x  32   ->   208 x 208 x  64
    3 max          2 x 2 / 2   208 x 208 x  64   ->   104 x 104 x  64
    4 conv    128  3 x 3 / 1   104 x 104 x  64   ->   104 x 104 x 128
    5 conv     64  1 x 1 / 1   104 x 104 x 128   ->   104 x 104 x  64
    6 conv    128  3 x 3 / 1   104 x 104 x  64   ->   104 x 104 x 128
    7 max          2 x 2 / 2   104 x 104 x 128   ->    52 x  52 x 128
    8 conv    256  3 x 3 / 1    52 x  52 x 128   ->    52 x  52 x 256
    9 conv    128  1 x 1 / 1    52 x  52 x 256   ->    52 x  52 x 128
   10 conv    256  3 x 3 / 1    52 x  52 x 128   ->    52 x  52 x 256
   11 max          2 x 2 / 2    52 x  52 x 256   ->    26 x  26 x 256
   12 conv    512  3 x 3 / 1    26 x  26 x 256   ->    26 x  26 x 512
   13 conv    256  1 x 1 / 1    26 x  26 x 512   ->    26 x  26 x 256
   14 conv    512  3 x 3 / 1    26 x  26 x 256   ->    26 x  26 x 512
   15 conv    256  1 x 1 / 1    26 x  26 x 512   ->    26 x  26 x 256
   16 conv    512  3 x 3 / 1    26 x  26 x 256   ->    26 x  26 x 512
   17 max          2 x 2 / 2    26 x  26 x 512   ->    13 x  13 x 512
   18 conv   1024  3 x 3 / 1    13 x  13 x 512   ->    13 x  13 x1024
   19 conv    512  1 x 1 / 1    13 x  13 x1024   ->    13 x  13 x 512
   20 conv   1024  3 x 3 / 1    13 x  13 x 512   ->    13 x  13 x1024
   21 conv    512  1 x 1 / 1    13 x  13 x1024   ->    13 x  13 x 512
   22 conv   1024  3 x 3 / 1    13 x  13 x 512   ->    13 x  13 x1024
   23 conv   1024  3 x 3 / 1    13 x  13 x1024   ->    13 x  13 x1024
   24 conv   1024  3 x 3 / 1    13 x  13 x1024   ->    13 x  13 x1024
   25 route  16
   26 reorg              / 2    26 x  26 x 512   ->    13 x  13 x2048
   27 route  26 24
   28 conv   1024  3 x 3 / 1    13 x  13 x3072   ->    13 x  13 x1024
   29 conv    425  1 x 1 / 1    13 x  13 x1024   ->    13 x  13 x 425
   30 detection
Loading weights from /root/yolo.weights...Done!
data/dog.jpg: Predicted in 0.844487 seconds.
dog: 57%
car: 52%
truck: 56%
car: 62%
bicycle: 59%
````


