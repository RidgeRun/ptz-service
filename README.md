##  PTZ Microservice 1.0.0

PTZ Microservice allows you to navigate a video through PTZ.

It leverages the RidgeRun [Spherical Video PTZ](https://developer.ridgerun.com/wiki/index.php/Spherical_Video_PTZ )
to make possible the selection of your region of interest within the sphere. This is specified through pan (horizontal), tilt (vertical), and zoom controls, which can be updated at any time during execution.

This service receives an RTSP stream, performs the PTZ depending on the user instructions, and then returns the stream using the same protocol, RTSP. By default the service uses the first VST
stream available as input and uses rtsp://<IP>:5021/ptz_out as output stream.

### API configuration

Take a look at the [API Documentation](api/openapi.yaml) for a list of the available requests.

### Running the service

Before running the service, you should make sure you have all the dependencies installed. The intructions to do it can be found [here](https://developer.ridgerun.com/wiki/index.php/Spherical_Video_PTZ/User_Guide/Building_and_Installation#)

The project is configured (via setup.py) to install the service with the name __ptz__. So to install it run:

```bash
pip install .
```

Then you will have the service with the following options:

```bash
usage: ptz [-h] [--port PORT] [--host HOST] [--ptz-window-size PTZ_WINDOW_SIZE]

options:
  -h, --help            show this help message and exit
  --port PORT           Port for server
  --host HOST           Server ip address
  --ptz-window-size PTZ_WINDOW_SIZE
                        Size of the PTZ output window in pixels. The final resolution will be (Size x Size)
```


## PTZ Microservice Docker

Before starting with docker support make sure you have nvidia runtime in your system. Follow [these instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration) to have docker up and runing in your Jetson Board.

### Build the container

We can build the ptz microservice container using the Dockerfile in the docker directory. This includes a base NVIDA image and the dependencies to run the ptz microservice application.

First, we need to prepare the context directory for this build, please create a directory and include all the needed repositories (listed below). The Dockerfile will look for all the source code in the context directory and copy them to the container.

```bash
ptz-context/
.
├── gst-cuda
├── gst-rr-panoramaptz
├── gst-rtsp-sink
├── libpanorama
├── ptz
└── rrms-utils
```

Then build the container image running the following command from the folder contaning the Dockerfile and context directory:

```bash
sudo docker build \
--network=host \
-f Dockerfile \
-t ridgerun/ptz-service:latest ptz-context/
```

Change __ptz-context__ to your context's path and the tag (-t) to the name you want to give to your image.

### Launch the container

The container can be launched by running the following command:


```bash
sudo docker run --runtime nvidia -it --privileged --net=host --ipc=host --name ptz-service  ridgerun/ptz-service:latest
```

You can modify the name you want to give to your container with the option __--name__.

Here we are creating a container called __ptz-service__ that will start the ptz-service application in the default address and port and using the default output resolution. If a different address, port, or output resolution has to be used, you can do it by running:

```bash
sudo docker run --runtime nvidia -it --privileged --net=host --ipc=host --name ptz-service  ridgerun/ptz-service:latest --host=HOST --port=PORT --ptz-window-size=PTZ_WINDOW_SIZE
```
