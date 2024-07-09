# Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

FROM nvcr.io/nvidia/l4t-base:r36.2.0

# Configure time zone
ENV TZ=America/Costa_Rica
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

# Add nvidia repositories
ADD --chown=root:root https://repo.download.nvidia.com/jetson/jetson-ota-public.asc /etc/apt/trusted.gpg.d/jetson-ota-public.asc
RUN chmod 644 /etc/apt/trusted.gpg.d/jetson-ota-public.asc \
    && apt-get update && apt-get install -y --no-install-recommends  ca-certificates \
    && echo "deb https://repo.download.nvidia.com/jetson/common r36.2 main" > /etc/apt/sources.list.d/nvidia-l4t-apt-source.list \
    && echo "deb https://repo.download.nvidia.com/jetson/t234 r36.2 main" >> /etc/apt/sources.list.d/nvidia-l4t-apt-source.list \
    && mkdir -p /opt/nvidia/l4t-packages/ \
    && touch /opt/nvidia/l4t-packages/.nv-l4t-disable-boot-fw-update-in-preinstall \
    && mkdir -p /lib/firmware && touch /lib/firmware/pva_auth_allowlist \
    && apt-get update \
    && yes N | apt-get install -y --no-install-recommends nvidia-l4t-core

RUN apt-get update && apt-get --yes install \
    sudo tree git ca-certificates \
    python3 python3-pip python3-setuptools \
    ninja-build \
    gcc cmake pkg-config build-essential automake autoconf gtk-doc-tools \
    libegl1-mesa-dev libtool

RUN pip3 install meson==0.60
RUN apt install -y libgstreamer1.0-dev
RUN apt install -y libgstreamer-plugins-base1.0-dev
RUN apt install -y libgstreamer-plugins-good1.0-dev
RUN apt install -y nvidia-l4t-jetson-multimedia-api
RUN apt install -y cuda-toolkit-12-2
RUN apt install -y libcublas-12-2
RUN apt install -y libcudnn8 libjansson4 libyaml-cpp-dev libjsoncpp-dev protobuf-compiler
RUN apt install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0

# Libpanorama dependencies
RUN apt install -y nvidia-opencv libjsoncpp-dev libopencv-dev
RUN pip3 install pre-commit

# Fix OpenCV Package config
RUN sed -i 's@prefix=/usr/local@prefix=/usr@g' /usr/lib/pkgconfig/opencv4.pc

# Add nvcc to path
ENV PATH=/usr/local/cuda/bin/:$PATH

#Copy and install gst-cuda
COPY gst-cuda /gst-cuda
WORKDIR /gst-cuda
RUN sed -i "s/#define EVAL_MAX_NUM_BUFFERS 1800/#define EVAL_MAX_NUM_BUFFERS 9000/g" gst-libs/sys/cuda/gstcudaeval.h
RUN ./autogen.sh --prefix=/usr/ --libdir=/usr/lib/aarch64-linux-gnu/ --enable-eval
RUN make
RUN make install

# Add libpanorama
COPY libpanorama /libpanorama
WORKDIR /libpanorama
RUN meson setup builddir \
    -Deval=enabled \
    -Drreval:eval-method=iter \
    -Drreval:eval-iterations-limit=9000 \
    -Dexamples=disabled \
    -Dtests=disabled \
    -Ddocs=disabled \
    -Dgstreamer=disabled \
    -Dqt=disabled \
    --prefix=/usr
RUN ninja -C builddir
RUN ninja -C builddir install

# Copy gst-rr-panoramaptz
COPY gst-rr-panoramaptz /gst-rr-panoramaptz

#Install rrpanoramaptz
WORKDIR /gst-rr-panoramaptz
RUN meson builddir -Ddocs=disabled --prefix=/usr
RUN ninja -C builddir
RUN ninja -C builddir install

#gst-rtsp-sink dependencies
RUN apt-get install -y libgstrtspserver-1.0-dev
RUN apt-get install -y libgstreamer1.0-dev
RUN apt-get install -y libgstreamer-plugins-base1.0-dev
RUN apt-get install -y libgstreamer-plugins-good1.0-dev
RUN apt-get install -y libgstreamer-plugins-bad1.0-dev

# Copy gst-rtsp-sink
COPY gst-rtsp-sink /gst-rtsp-sink

#Install gst-rtspsink
WORKDIR /gst-rtsp-sink
RUN meson setup builddir \
    -Deval-mode=true  \
    -Drreval:eval-method=iter \
    -Drreval:eval-iterations-limit=9000 \
    --prefix=/usr
RUN ninja -C builddir
RUN ninja -C builddir install

# Install rrms-utils
COPY rrms-utils /rrms-utils
RUN cd /rrms-utils && pip3 install .

# Install ptz
COPY ptz /ptz
RUN cd /ptz && pip3 install .

WORKDIR /root/

# Remove Source code
RUN rm -r /libpanorama
RUN rm -r /gst-rtsp-sink
RUN rm -r /gst-rr-panoramaptz
RUN rm -r /gst-cuda
RUN rm -r /rrms-utils
RUN rm -r /ptz

# Remove libpanorama headers
RUN rm -r /usr/include/libpanorama*

# Set entry point to the service
ENTRYPOINT ["ptz"]
