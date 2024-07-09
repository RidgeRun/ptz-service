#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Controller for PTZ position
"""

from flask import request
from flask_cors import cross_origin
from rrmsutils.models.apiresponse import ApiResponse
from rrmsutils.models.ptz.position import Position

from ptz.controllers.controller import Controller
from ptz.logger import Logger
from ptz.ptz import PTZ

logger = Logger.get_logger()


class PositionController(Controller):
    """Controller for PTZ position
    """

    def __init__(self, ptz: PTZ):
        """Constructor of the Class PositionController

        Args:
            ptz (PTZ): a PTZ Class instaance
        """
        self.__ptz = ptz

    def add_rules(self, app):
        """Add rules

        Args:
            app (Flask): Flask application
        """
        app.add_url_rule('/position', 'position',
                         self.position, methods=['GET', 'PUT'])

    @cross_origin()
    def position(self):
        """Defines the action based in the type of method in the request

        Returns:
            method: get or put position
        """
        if request.method == 'PUT':
            return self.put_position()
        if request.method == 'GET':
            return self.get_position()

        data = ApiResponse(
            code=1, message=f'Method {request.method} not supported').model_dump_json()
        return self.response(data, 400)

    def get_position(self):
        """Get the current PTZ position

        Returns:
            json: json with the current position, or json with an error if there is an exception.
        """

        set_position_result = self.__ptz.get_position()

        if set_position_result is None:
            response = ApiResponse(
                code=1, message='Error getting Position from the pipeline')
            data = response.model_dump_json()
            return self.response(data, 400)

        try:
            data = set_position_result.model_dump_json()
        except Exception as e:  # pylint: disable=broad-exception-caught
            response = ApiResponse(
                code=1, message=f'Error getting Position from the pipeline, error: {repr(e)}')
            data = response.model_dump_json()
            return self.response(data, 400)
        logger.info(f'Getting Position {data}')
        return self.response(data, 200)

    def put_position(self):
        """Set the current position according to the json included in request content

        Returns:
            json: json with the position to set in the pipeline, or with an error if there is an exception.
        """
        data = request.json
        try:
            position = Position.model_validate(data)
        except Exception as e:  # pylint: disable=broad-exception-caught
            response = ApiResponse(
                code=1, message=f'Error setting Position in the pipeline, error: {repr(e)}')
            data = response.model_dump_json()
            return self.response(data, 400)

        set_position_result = self.__ptz.set_position(position)

        if set_position_result is False:
            logger.error('Error setting position')
            response = ApiResponse(
                code=1, message='Error setting Position in the pipeline')
            data = response.model_dump_json()
            return self.response(data, 400)

        data = position.model_dump_json()
        logger.info(f'Setting Position to {data}')
        return self.response(data, 200)
