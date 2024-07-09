#  Copyright (C) 2024 RidgeRun, LLC (http://www.ridgerun.com)
#  All Rights Reserved.
#
#  The contents of this software are proprietary and confidential to RidgeRun,
#  LLC.  No part of this program may be photocopied, reproduced or translated
#  into another programming language without prior written consent of
#  RidgeRun, LLC.  The user is free to modify the source code after obtaining
#  a software license from RidgeRun.  All source code changes must be provided
#  back to RidgeRun without any encumbrance.

"""Media Class
"""
import time
from threading import Thread

import gi
from gi.repository import GLib, GObject, Gst

from ptz.logger import Logger

gi.require_version('Gst', '1.0')
Gst.init(None)

logger = Logger.get_logger()


class Media():
    """Media Class, sets a Gstreamer pipeline, change its status, updates and gets the properties of the element specified
    """

    def __init__(self, description: str, retry: bool = True, retry_delay: int = 5):
        """Constructor of the Class Media

        Args:
            description (str): specifies the description of the pipeline to play #update documentation #
            retry (bool, optional): Whether or not to try to reconnect in case of any error. Defaults to True.
            retry_delay (int, optional): Time in seconds to wait before trying to reconnect (valid only if retry is True). Defaults to 5.
        """
        self.__description = description
        self.__retry = retry
        self.__retry_delay = retry_delay
        self.__mainloop = GObject.MainLoop()
        self.__thread = Thread(target=self.__loop)
        self.__thread.start()
        self.__create()

    def __create(self):
        try:
            self.__pipeline = Gst.parse_launch(self.__description)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f'Error creating pipeline: {e}')
            raise

        if self.__retry:
            bus = self.__pipeline.get_bus()
            bus.add_watch(GLib.PRIORITY_DEFAULT, self.__bus_callback)

    def __del__(self):
        self.stop()
        self.__mainloop.quit()
        self.__thread.join()

    def __loop(self):
        self.__mainloop.run()

    def __delayed_start(self):
        time.sleep(self.__retry_delay)
        logger.info("Reconecting ...")
        self.__create()
        self.play()

    def __bus_callback(self, bus, message):  # pylint: disable=unused-argument
        if message.type == Gst.MessageType.ERROR:
            logger.warning(f"Something went wrong: {message.parse_error()}")
            logger.info("Scheduling stream reconnection...")
            self.stop()
            t = Thread(target=self.__delayed_start)
            t.start()

        return True

    def stop(self):
        """Stops (change the state) the pipeline played before
        Returns:
            True or Flase: True is stop is successful, False if not
        """
        if self.__pipeline is None:
            logger.warning('There is no pipeline created')
            return False

        stoping_result = self.__pipeline.set_state(Gst.State.NULL)

        if stoping_result == Gst.StateChangeReturn.FAILURE:
            logger.error('Error stoping the pipeline')
            return False
        logger.info(f'Stoping {self.__description}')
        return True

    def play(self):
        """Plays (change the state) of the parsed pipeline
        Returns:
            True or Flase: True is stop is successful, False if not
        """
        if self.__pipeline is None:
            logger.warning('There is no pipeline created')
            return False

        playing_result = self.__pipeline.set_state(Gst.State.PLAYING)

        if playing_result == Gst.StateChangeReturn.FAILURE:
            logger.error('Error playing the pipeline')
            return False
        logger.info(f'Playing {self.__description}')
        return True

    def set_property(self, element_name, property_name, value):
        """Set the 'property_name' in the pipeline 'element_name' to the specified 'value'

        Args:
            element_name (str): Pipeline element to be changed
            property_name (str): Property in the pipeline element to be changed
            value (str or float): Value to be set in the property that belongs to the element in the pipeline

        Returns:
            True, Flase:  True if the pipeline element actually is in the pipeline. False if doesn't.
        """

        element = self.__pipeline.get_by_name(element_name)
        if element is None:
            logger.warning(f'There is no {element_name} in the pipeline')
            return False

        try:
            element.set_property(property_name, value)
        except Exception as e:
            logger.error(f'Error setting the property, {property_name}: {e}')
            return False

        logger.info(f'Setting {property_name} to {value}')
        return True

    def get_property(self, element_name, property_name):
        """Gets the value of an elements property in the pipeline

        Args:
            element_name (str): Pipeline element to get the property from
            property_name (str): Property in the pipeline element to get the value from

        Returns:
            property, Noner: property; the value of the  elements property asked for, None if the element doesn't exist in the pipeline.
        """
        element = self.__pipeline.get_by_name(element_name)
        if element is None:
            logger.warning(f'There is no {element_name} in the pipeline')
            return None

        try:
            get_result = element.get_property(property_name)
        except Exception as e:
            logger.error(f'Error getting the property, {property_name}: {e}')
            return None

        logger.info(f'Getting {property_name}')
        return get_result
