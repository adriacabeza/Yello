FROM ubuntu:18.04 

MAINTAINER adriacabeza
 
# WORKING DIRECTORY
WORKDIR /root

# DARKNET
## INSTALL
RUN \
	apt-get update && apt-get install -y \
	autoconf \
	automake \
	mplayer \
	libtool \
	vim \ 
	tmux \
	build-essential \
	git \
	python-pip \
	python-dev \
	pkg-config \
	wget  \
 	libavdevice-dev \
	libavfilter-dev \
	libavformat-dev \
	libavcodec-dev \
	libavutil-dev \
	libswscale-dev \
	libavresample-dev 

## BUILD REPOSITORY
RUN \
	git clone https://github.com/pjreddie/darknet && \
	cd darknet && \
	make

## DOWNLOAD TINY YOLO WEIGHTS 
RUN \
	wget https://pjreddie.com/media/files/yolov3-tiny.weights  >/dev/null 2>&1

## TESTING 
RUN \
	cd darknet/ && \
	./darknet && \
	./darknet detector test cfg/coco.data cfg/yolov3-tiny.cfg /root/yolov3-tiny.weights data/dog.jpg


# YELLO
## BUILD REPOSITORY
RUN \
	git clone https://github.com/adriacabeza/Yello.git 

# INSTALL DEPENDENCIES
ADD requirements.txt .
RUN pip install -r requirements.txt 


# default command
CMD ["bash"]



