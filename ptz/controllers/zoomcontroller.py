#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Controller for Zoom
"""

from flask import request
from flask_cors import cross_origin
from rrmsutils.models.apiresponse import ApiResponse
from rrmsutils.models.ptz.zoom import Zoom

from ptz.controllers.controller import Controller
from ptz.logger import Logger
from ptz.ptz import PTZ

logger = Logger.get_logger()


class ZoomController(Controller):
    """Controller for Zoom
    """

    def __init__(self, ptz: PTZ):
        """Constructor of the Class ZoomController

        Args:
            ptz (PTZ): a PTZ Class instaance
        """
        self.__ptz = ptz

    def add_rules(self, app):
        """Add rules

        Args:
            app (Flask): Flask application
        """
        app.add_url_rule('/zoom', 'zoom',
                         self.zoom, methods=['GET', 'PUT'])

    @cross_origin()
    def zoom(self):
        """Defines the action based in the type of method in the request

        Returns:
            method: get or put zoom
        """
        if request.method == 'PUT':
            return self.put_zoom()
        if request.method == 'GET':
            return self.get_zoom()

        data = ApiResponse(
            code=1, message=f'Method {request.method} not supported').model_dump_json()
        return self.response(data, 400)

    def get_zoom(self):
        """Get the current Zoom

        Returns:
            json: json with the current zoom, or json with an error if there is an exception.
        """

        get_zoom_result = self.__ptz.get_zoom()

        if get_zoom_result is None:
            response = ApiResponse(
                code=1, message='Error getting Zoom in the pipeline')
            data = response.model_dump_json()
            return self.response(data, 400)

        try:
            data = get_zoom_result.model_dump_json()
        except Exception as e:  # pylint: disable=broad-exception-caught
            response = ApiResponse(
                code=1, message=f'Error getting Zoom from the pipeline, error: {repr(e)}')
            data = response.model_dump_json()
            return self.response(data, 400)
        logger.info(f'Getting Zomm {data}')
        return self.response(data, 200)

    def put_zoom(self):
        """Set the current Zoom according to the json included in request content

        Returns:
            json : json with the zoom to set in the pipeline, or with an error message.
        """
        data = request.json
        try:
            zoom = Zoom.model_validate(data)
        except Exception as e:  # pylint: disable=broad-exception-caught
            response = ApiResponse(
                code=1, message=f'Error setting Zoom, error: {repr(e)}')
            data = response.model_dump_json()
            return self.response(data, 400)

        set_zoom_result = self.__ptz.set_zoom(zoom)

        if set_zoom_result is False:
            logger.error('Error setting zoom')
            response = ApiResponse(
                code=1, message='Error setting Zoom in the pipeline')
            data = response.model_dump_json()
            return self.response(data, 400)

        data = zoom.model_dump_json()
        logger.info(f'Setting Zoom to {data}')
        return self.response(data, 200)
