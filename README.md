# Yello (Yolo + DJI Tello)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/adriacabeza/Yello.js.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/adriacabeza/Yello.js/stargazers/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/adriacabeza/Yello/pulls)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/adriacabeza/Yello)


This repository contains a project that combines DJI Tello and Deep Learning (Tiny Yolo). The aim of this project is to   detect several objects using the drone. It uses [Darknet](https://github.com/pjreddie/darknet): an open source neural network framework written in C and CUDA) and [TelloPy](https://github.com/hanyazou/TelloPy) : a super friendly api for the drone. 

Although  the weights of the model can be changed, I used the ones pretrained from the official website ([YOLOv3- tiny](https://pjreddie.com/media/files/yolov3-tiny.weights)). 



Moreover, you can add functionalities easily in the project. Already implemented functionalities:

- Whenever it detects a person it takes a photo

## Installation

First you have to clone the repository. 
To continue you need to have docker installed (follow the instructions here https://docs.docker.com/install/). Then, to build the docker write in the repository folder: 
``` 
docker build --no-cache -t yello .
```
> NOTE: It can last several minutes to finish building.
Then you will be able to do run the docker by typing:

```
docker run --rm -it --name yello bash
```

To test if everything went correct, you can run a test with tiny-yolo:
````
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
````


## Execute orders to the drone

To execute orderts to the drone, you have to send packets with the hex code of the instruction that is desired. Here there is the table of codes:

| Code   | Instruction |
|--------|-------------|
| 0x0054 | Take off    |
| 0x0055 | Land        |
| 0x005e | Palm Land   |
| 0x0030 | Take Picture|
| 0x005d | Throw & Go  |

 And here a code snippet of how to do it:
```python
drone = tellopy.Tello()
drone.connect()
drone.wait_for_connection(60.0)
pkt = Packet(0x0054)
pkt.fixup()
drone.send_packet(pkt)
```
However it really depends on what you want to do since there are several different structures of packets. For more information please look at the [docs](https://github.com/adriacabeza/Yello/tree/master/docs/README.md)

## Demo video with Tiny-Yolo
