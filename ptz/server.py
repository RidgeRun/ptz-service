#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Server
"""

from flask import Flask


class Server():
    """Flask server class
    """

    def __init__(self, controllers: list, host='127.0.0.1', port=5000):
        """Create a REST server

        Args:
            controllers (list): controller list used by server
            host (str, optional): Server IP address. Defaults to '127.0.0.1'.
            port (int, optional): Server PORT. Defaults to 5000.
        """
        self.app = Flask(__name__)

        # Add rules
        for controller in controllers:
            controller.add_rules(self.app)

        self.host = host
        self.port = port

    def run(self):
        """Start the server. This is a blocking method.
        """
        self.app.run(host=self.host, port=self.port)
