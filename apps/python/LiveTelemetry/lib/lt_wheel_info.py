#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one wheel infos from car and draw on screen.

@author: albertowd
"""
import copy
import sys

import ac

from lib.lt_colors import Colors
from lib.lt_components import BoxComponent, Camber, Dirt, Height, Load, Pressure, Temps, Suspension, Tire, Wear
from lib.lt_util import WheelPos
from lib.sim_info import info


class Data(object):

    def __init__(self):
        self.camber = 0.0
        self.height = 0.0
        self.susp_m_t = 1.0
        self.susp_t = 0.0
        self.timestamp = 0
        self.tire_d = 0.0
        self.tire_p = 0.0
        self.tire_t_c = 0.0
        self.tire_t_i = 0.0
        self.tire_t_m = 0.0
        self.tire_t_o = 0.0
        self.tire_w = 0.0

    def update(self, wheel, info):
        index = wheel.index()
        self.camber = info.physics.camberRAD[index]

        # If there's no max travel, keep it 50%.
        self.susp_t = info.physics.suspensionTravel[index]
        max_travel = info.static.suspensionMaxTravel[index]
        self.susp_m_t = max_travel if max_travel > 0.0 else (self.susp_t * 2.0)

        # um to mm
        self.height = info.physics.rideHeight[int(index / 2)] * 1000.0

        # Get susp diff
        susp_diff = self.susp_t - \
            info.physics.suspensionTravel[index +
                                          (1 if wheel.is_left() else -1)]
        self.height -= ((susp_diff / 2.0) * 1000.0)

        self.timestamp = info.graphics.iCurrentTime
        self.tire_d = info.physics.tyreDirtyLevel[index] * 4.0

        # N to (5*kgf)
        self.tire_l = info.physics.wheelLoad[index] / (5.0 * 9.80665)
        self.tire_p = info.physics.wheelsPressure[index]
        self.tire_t_c = info.physics.tyreCoreTemperature[index]
        self.tire_t_i = info.physics.tyreTempI[index]
        self.tire_t_m = info.physics.tyreTempM[index]
        self.tire_t_o = info.physics.tyreTempO[index]

        # Normal to percent
        self.tire_w = info.physics.tyreWear[index] / 100.0


class WheelInfo(object):
    """ Wheel info to draw and update each wheel. """

    def __init__(self, acd, configs, wheel_index):
        """ Default constructor receive the index of the wheel it will draw info. """
        self.__wheel = WheelPos(wheel_index)
        self.__active = False
        self.__data = Data()
        self.__data_log = []
        self.__info = info
        self.__options = {
            "Camber": configs.get_bool_option("Camber"),
            "Dirt": configs.get_bool_option("Dirt"),
            "Height": configs.get_bool_option("Height"),
            "Load": configs.get_bool_option("Load"),
            "Logging": configs.get_bool_option("Logging"),
            "Pressure": configs.get_bool_option("Pressure"),
            "Suspension": configs.get_bool_option("Suspension"),
            "Temps": configs.get_bool_option("Temps"),
            "Tire": configs.get_bool_option("Tire"),
            "Wear": configs.get_bool_option("Wear")
        }
        self.__window_id = ac.newApp(
            "Live Telemetry {}".format(self.__wheel.name()))
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        position = configs.get_window_position(self.__wheel.name())
        ac.setPosition(self.__window_id, *position)

        size = configs.get_option("Size")
        mult = BoxComponent.resolution_map[size]
        ac.setSize(self.__window_id, 512 * mult, 271 * mult)

        self.__components = []
        self.__components.append(Temps(acd, size, self.__wheel))
        self.__components.append(Dirt(size))
        self.__components.append(Tire(acd, size, self.__wheel))

        self.__components.append(Camber(size))
        self.__components.append(Suspension(size, self.__wheel))
        self.__components.append(Height(size, self.__wheel, self.__window_id))
        self.__components.append(
            Pressure(acd, size, self.__wheel, self.__window_id))
        self.__components.append(Wear(size, self.__wheel))
        # Needs to be the last to render above all components
        self.__components.append(Load(size, self.__wheel))

        # Only draw after the setup
        self.set_active(configs.is_window_active(self.__wheel.name()))

    def get_data_log(self):
        """ Returns the saved data from the session. """
        return self.__data_log

    def get_id(self):
        """ Returns the wheel id. """
        return self.__wheel.name()

    def get_option(self, name):
        """ Returns an option value. """
        return self.__options[name]

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def has_data_logged(self):
        """Returns if the info has data logged."""
        return len(self.__data_log) > 0

    def is_active(self):
        """ Returns window status. """
        return self.__active

    def draw(self):
        """ Draws all info on screen. """
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        for component in self.__components:
            if self.__options[type(component).__name__] == True:
                ac.glColor4f(*Colors.white)
                component.draw(self.__data)
            else:
                component.clear()
        ac.glColor4f(*Colors.white)

    def resize(self, resolution):
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 271 * mult)
        for component in self.__components:
            component.resize(resolution)

    def set_active(self, active):
        """ Toggles the window status. """
        self.__active = active

    def set_option(self, name, value):
        """ Updates an option value. """
        self.__options[name] = value

    def update(self):
        """ Updates the wheel information. """
        self.__data.update(self.__wheel, self.__info)
        if self.__options["Logging"] == True:
            self.__data_log.append(copy.copy(self.__data))

        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.update(self.__data)
