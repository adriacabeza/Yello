# Yello (Yolo + DJI Tello)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/adriacabeza/Yello.js.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/adriacabeza/Yello.js/stargazers/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)


This repository contains a project that combines DJI Tello and Deep Learning (Tiny Yolo). The aim of this project is to   detect several objects using the drone. It uses [Darknet](https://github.com/pjreddie/darknet): an open source neural network framework written in C and CUDA) and [TelloPy](https://github.com/hanyazou/TelloPy) : a super friendly api for the drone. 

Although  the weights of the model can be changed, I used the ones pretrained from the official website ([YOLOv3- tiny](https://pjreddie.com/media/files/yolov3-tiny.weights)). 



Moreover, you can add functionalities easily in the project. Already implemented functionalities:

- Whenever it detects a person it takes a photo


