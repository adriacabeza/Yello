# Yello (Yolo + DJI Tello)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/adriacabeza/Yello/pulls)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)


<p align="center">
<img src="images/yello.gif"/>
</p>

>Note: Those weirds moments in the video are sideflips


This repository contains a project that combines DJI Tello and Deep Learning (Tiny Yolo). The aim of this project is to detect several objects using the drone. It uses [Darkflow](https://github.com/thtrieu/darkflow): an open source project that translates darknet to tensorflow) and [TelloPy](https://github.com/hanyazou/TelloPy) : a super friendly api for the drone. A lot of work can still be done tho (this is just a toy thing) i.e. set actions when something is detected like take a photo when it sees a person, properly set the commands or test that everything works (lol). 


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
5. Install mencoder to record videos
6. Then, after setting a connection to the drone and preparing the video stream you can run it and one window will show up with the predictions. 

```python
python3 src/yello.py
```

<p align="center">
<img src="images/from_scratch.gif">
</p>

#### Controls

```python
controls = {
    'w': lambda: drone.forward(5),
    'a': lambda: drone.left(5),
    's': lambda:  drone.backward(5),
    'd': lambda: drone.right(5),
    'i': lambda: drone.flip_forward(),
    'k': lambda: drone.flip_back(),
    'j': lambda: drone.flip_left(),
    'l': lambda: drone.flip_right(),
    'Key.left': lambda : drone.counter_clockwise(10),
    'Key.right': lambda : drone.clockwise(10),
    'Key.up': lambda : drone.up(10),
    'Key.down': lambda : drone.down(10),
    'Key.tab': lambda: drone.takeoff(),
    'Key.backspace': lambda: drone.land(),
    'p': lambda: drone.palm_land(),
    'Key.enter': lambda: drone.take_picture(),
    'v': lambda: toggle_recording(),
    'c': lambda: drone.clockwise_degrees(360),
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


