#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""main
"""

import argparse

from ptz.controllers.positioncontroller import PositionController
from ptz.controllers.streamcontroller import StreamController
from ptz.controllers.zoomcontroller import ZoomController
from ptz.logger import Logger
from ptz.ptz import PTZ
from ptz.server import Server


def parse_args():
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5010,
                        help="Port for server")
    parser.add_argument("--host", type=str, default='127.0.0.1',
                        help="Server ip address")
    parser.add_argument("--ptz-window-size", type=int, default=500,
                        help="Size of the PTZ output window in pixels. The final resolution will be (Size x Size)")
    args = parser.parse_args()

    return args


def main():
    """main application
    """
    Logger.init()

    args_m = parse_args()
    controllers = []
    ptz = PTZ(window_size=args_m.ptz_window_size)
    controllers.append(PositionController(ptz))
    controllers.append(ZoomController(ptz))
    controllers.append(StreamController(ptz))
    server = Server(controllers, host=args_m.host, port=args_m.port)
    server.run()


if __name__ == "__main__":
    main()
