FROM ubuntu:18.04 

MAINTAINER adriacabeza
 
# WORKING DIRECTORY
WORKDIR /root

# DARKNET

# INSTALL
RUN \
	apt-get update && apt-get install -y \
	autoconf \
	automake \
	libtool \
	build_essential \
	git \
	python-pip \
	wget && \
	

# BUILD REPOSITORY
RUN \
	git clone https://github.com/pjreddie/darknet && \
	cd darknet && \
	make

# DOWNLOAD TINY YOLO WEIGHTS 
RUN \
	wget https://pjreddie.com/media/files/yolov3-tiny.weights  >/dev/null 2>&1

# TESTING 
RUN \
	cd darknet/ && \
	./darknet && \
	./darknet detector test cfg/coco.data cfg/yolo3-tiny.cfg /root/yolov3-tiny.weights 

# TELLOPY

# BUILD REPOSITORY 
RUN \ 



# default command
CMD ["bash"]



