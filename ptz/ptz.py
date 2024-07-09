#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Class PTZ
"""

from mmj_utils.vst import VST
from rrmsutils.models.ptz.position import Position
from rrmsutils.models.ptz.stream import Stream
from rrmsutils.models.ptz.zoom import Zoom

from ptz.logger import Logger
from ptz.media import Media

logger = Logger.get_logger()


class PTZ():
    """Class PTZ, defines the functions of pan, tilt, and zoom.
    """

    def __init__(self, vst_uri="http://127.0.0.1:81", window_size: int = 500):
        """PTZ object. It receives an input rtsp stream, performs pan, tilt and zoom (PTZ) operations
        on it and generates a new rtsp stream with the result. The input video can be given as a regular
        rtsp URI or an NVIDIA VST stream name.

        Args:
            vst_uri (str, optional): The URL of NVIDIA VST service. Defaults to "http://127.0.0.1:81".
            window_size (int, optional): The size in pixels of the output PTZ window. The resolution in pixels will be (Size x Size). Defaults to 500.
        """
        self.__in_uri = None
        self.__out_port = None
        self.__out_mapping = None
        self.__media = None
        self.__vst_uri = vst_uri
        self.__window_size = window_size

        self.set_stream(Stream(in_uri="", out_port=5021, out_mapping="ptz_out"))

    def get_position(self):
        """Get the position (pan and tilt) in the rrpanorama ptz pipeline element

        Returns:
            json, None: json -> contanis the obtained pan and tilt values, None if the element doesn't exist in the pipeline.
        """
        if self.__media is None:
            logger.warning('There is no pipeline created yet')
            return None

        pan_obtained = self.__media.get_property('rr_panorama_ptz', 'pan')

        if pan_obtained is None:
            logger.error('Error getting pan')
            return None

        tilt_obtained = self.__media.get_property('rr_panorama_ptz', 'tilt')

        if tilt_obtained is None:
            logger.error('Error getting tilt')
            return None

        logger.info('Getting position from de pipeline')
        return Position(pan=pan_obtained, tilt=tilt_obtained)

    def set_position(self, position: Position):
        """Set the position (pan and tilt) in the rrpanorama ptz pipeline element

        Args:
            position (Position): a json file that contains the pan and tilt values to set in the pipeline element

        Returns:
            True or False: True if the position is successfully set, False if the element doesn't exist in the pipeline
        """

        if self.__media is None:
            logger.warning('There is no pipeline created yet')
            return False

        set_pan_result = self.__media.set_property(
            'rr_panorama_ptz', 'pan', position.pan)

        if set_pan_result is False:
            logger.error('Error setting pan in the pipeline')
            return False

        set_tilt_result = self.__media.set_property(
            'rr_panorama_ptz', 'tilt', position.tilt)

        if set_tilt_result is False:
            logger.error('Error setting tilt in the pipeline')
            return False

        logger.info(f'Setting Position to {position}')
        return True

    def get_zoom(self):
        """Get the Zomm in the rrpanorama ptz pipeline element

        Returns:
            json, None: json -> contanis the obtained pan and tilt values, None if the element doesn't exist in the pipeline
        """
        if self.__media is None:
            logger.warning('There is no pipeline created yet')
            return None

        zoom_obtained = self.__media.get_property(
            'rr_panorama_ptz', 'zoom')

        if zoom_obtained is None:
            logger.error('Error getting zoom')
            return None

        logger.info('Getting zoom')
        return Zoom(zoom=zoom_obtained)

    def set_zoom(self, zoom: Zoom):
        """Set the zoom in the rrpanorama ptz pipeline element

        Args:
            zoom (Zoom): a json file that contains the zoom value to set in the pipeline element

        Returns:
            True or False: True if the zoom is successfully set and False if the element doesn't exist in the pipeline
        """
        if self.__media is None:
            logger.warning('There is no pipeline created yet')
            return False

        set_zoom_result = self.__media.set_property(
            'rr_panorama_ptz', 'zoom', zoom.zoom)

        if set_zoom_result is False:
            logger.error('Error setting zoom')
            return False

        logger.info(f'Setting zoom to {zoom}')
        return True

    def get_stream(self):
        """Get the in_stream, the out_port and the out_mapping in the pipeline

        Returns:
            json, None: json -> contanis the obtained pan and tilt values, None if the element doesn't exist in the pipeline.
        """
        if self.__media is None:
            logger.warning('There is no pipeline created yet')
            return None

        in_uri_obtained = self.__media.get_property('src', 'location')

        if in_uri_obtained is None:
            logger.error('Error getting in_uri')
            return None

        out_port_obtained = self.__media.get_property(
            'rtspsink', 'service')

        if out_port_obtained is None:
            logger.error('Error getting out_port')
            return None

        out_mapping_obtained = self.__out_mapping

        if out_mapping_obtained is None:
            logger.error('Error getting out_mapping')
            return None

        logger.info('Getting: in_uri, out_port and out_mapping')
        return Stream(in_uri=in_uri_obtained, out_port=out_port_obtained, out_mapping=out_mapping_obtained)

    def __get_vst_stream(self, name):
        try:
            vst = VST(self.__vst_uri)

            vst_rtsp_streams = vst.get_rtsp_streams()
            if len(vst_rtsp_streams) == 0:
                logger.warning("VST doesn't have active streams")
                return None
        except Exception as e:
            logger.error(f'Error getting VST stream {repr(e)}')
            return None

        stream = None
        for rtsp_stream in vst_rtsp_streams:
            if rtsp_stream['name'] == name:
                stream = rtsp_stream['url']
                break

        if not stream:
            stream = vst_rtsp_streams[0]['url']

        return stream

    def set_stream(self, stream: Stream):
        """Set the in_stream, the out_port and the out_mapping in the pipeline

        Args:
            stream (Stream): a json file that contains the stream value to set in the pipeline element

        Returns:
            json, False, or error: json -> contanis the obtained pan and tilt values, False if the element doesn't exist in the pipeline, or error if there is an exception.
        """

        if stream.in_uri.startswith("rtsp://"):
            self.__in_uri = stream.in_uri
        else:
            stream_uri = self.__get_vst_stream(stream.in_uri)
            if stream_uri is None:
                logger.warning(f"VST doesn't have a stream {stream.in_uri}")
                return False

            self.__in_uri = stream_uri
            logger.info(f"Using VST uri {stream} for {stream.in_uri}")

        self.__out_port = stream.out_port
        self.__out_mapping = stream.out_mapping

        try:
            d = self.__window_size
            pipeline = f'rtspsrc name=src latency=10 location={self.__in_uri} ! queue !  rtph264depay ! \
                         h264parse !  nvv4l2decoder ! capssetter caps=video/x-raw,framerate=30/1 ! \
                         queue ! nvvidconv ! queue ! rrpanoramaptz name=rr_panorama_ptz ! video/x-raw,width={d},height={d} ! \
                         queue ! nvvidconv !  queue !  nvv4l2h264enc  idrinterval=30  insert-sps-pps=true ! \
                         capsfilter name=capsfilter caps="video/x-h264,framerate=30/1,mapping={self.__out_mapping}" !  \
                         queue ! rtspsink name=rtspsink service={self.__out_port}'
            self.__media = Media(pipeline)
        except Exception as e:
            logger.error(f'Error parsing the pipeline, error: {repr(e)}')
            return False

        media_play_result = self.__media.play()

        if media_play_result is False:
            logger.error('Error playing the pipeline')
            return False

        return True
