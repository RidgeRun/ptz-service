#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Controller for input stream
"""

from flask import request
from flask_cors import cross_origin
from rrmsutils.models.apiresponse import ApiResponse
from rrmsutils.models.ptz.stream import Stream

from ptz.controllers.controller import Controller
from ptz.logger import Logger
from ptz.ptz import PTZ

logger = Logger.get_logger()


class StreamController(Controller):
    """Controller for input stream
    """

    def __init__(self, ptz: PTZ):
        """Constructor of the Class StreamController

        Args:
            ptz (PTZ): a PTZ Class instaance
        """
        self.__ptz = ptz

    def add_rules(self, app):
        """Add rules

        Args:
            app (Flask): Flask application
        """
        app.add_url_rule('/stream', 'stream',
                         self.stream, methods=['GET', 'PUT'])

    @cross_origin()
    def stream(self):
        """Defines the action based in the type of method in the request

        Returns:
            method: get or put stream
        """
        if request.method == 'PUT':
            return self.put_stream()
        if request.method == 'GET':
            return self.get_stream()

        data = ApiResponse(
            code=1, message=f'Method {request.method} not supported').model_dump_json()
        return self.response(data, 400)

    def get_stream(self):
        """Get the current stream

        Returns:
            json: json with the current in_uri, out_port, and out_mapping, or json with error if there is an exception.
        """

        get_stream_result = self.__ptz.get_stream()

        if get_stream_result is None:
            response = ApiResponse(
                code=1, message='Error getting: in_uri, out_port and out_mapping; in the pipeline')
            data = response.model_dump_json()
            return self.response(data, 400)

        try:
            data = get_stream_result.model_dump_json()
        except Exception as e:  # pylint: disable=broad-exception-caught
            response = ApiResponse(
                code=1, message=f'Error getting: in_uri, out_port and out_mapping; in the pipeline, error: {repr(e)}')
            data = response.model_dump_json()
            return self.response(data, 400)
        logger.info(
            f'Getting: in_uri, port_out and mapping_out: {data}')
        return self.response(data, 200)

    def put_stream(self):
        """Set the current stream according to the json included in request content

        Returns:
            json: json with the in_uri, out_port, and out_mapping to set in the pipeline, or json with error if there is an exception.
        """
        data = request.json

        try:
            stream = Stream.model_validate(data)
        except Exception as e:  # pylint: disable=broad-exception-caught
            response = ApiResponse(
                code=1, message=f'Error setting the in_uri, out_por and out_mapping, error: {repr(e)}')
            data = response.model_dump_json()
            logger.error(
                f'Error setting the in_uri, out_por and out_mapping, error: {repr(e)}')
            return self.response(data, 400)

        set_stream_result = self.__ptz.set_stream(stream)

        if set_stream_result is False:
            logger.error(
                'Error setting the in_uri, out_por and out_mapping')
            response = ApiResponse(
                code=1, message='Error settin in_uri, out_port, out_mapping')
            data = response.model_dump_json()
            return self.response(data, 400)

        data = stream.model_dump_json()
        logger.info(f'Setting in_uri, out_port, out_mapping to {data}')
        return self.response(data, 200)
