#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to update one engine infos from car and draw on screen.
"""
from lt_colors import Colors
from lt_config import Config
from lt_components import BoxComponent, RPMPower
from lt_sim_info import info

try:
    import ac
except:
    from lt_ac import ac


class Data(object):

    def __init__(self):
        self.max_power = 0.0
        self.max_rpm = 0.0
        self.max_torque = 0.0
        self.rpm = 0.0

    def update(self, info):
        self.max_power = info.static.maxPower
        self.max_rpm = info.static.maxRpm
        self.max_torque = info.static.maxTorque
        self.rpm = info.physics.rpms


class EngineInfo(object):
    """ Engine info to draw and update. """

    def __init__(self):
        """ Default constructor. """
        configs = Config()

        self.__active = False
        self.__data = Data()
        self.__info = info
        self.__window_id = ac.newApp("Live Telemetry Engine")
        ac.drawBorder(self.__window_id, 0)
        ac.setBackgroundColor(self.__window_id, 1.0, 1.0, 1.0)
        ac.setBackgroundOpacity(self.__window_id, 0.0)
        ac.setIconPosition(self.__window_id, 0, -10000)
        ac.setTitle(self.__window_id, "")

        pos_x = configs.get_engine_x()
        pos_y = configs.get_engine_y()
        ac.setPosition(self.__window_id, pos_x, pos_y)

        resolution = configs.get_resolution()
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 85 * mult)

        self.__bt_resolution = ac.addButton(self.__window_id, resolution)
        ac.setSize(self.__bt_resolution, 50, 30)
        ac.setFontAlignment(self.__bt_resolution, "center")

        self.__components = []
        self.__components.append(RPMPower(resolution, self.__window_id))

        self.set_active(configs.is_engine_active())

    def get_position(self):
        """ Returns the window position. """
        return ac.getPosition(self.__window_id)

    def get_button_id(self):
        """ Returns the resolution button id. """
        return self.__bt_resolution

    def get_window_id(self):
        """ Returns the window id. """
        return self.__window_id

    def is_active(self):
        """ Returns window status. """
        return self.__active

    def draw(self):
        """ Draws all info on screen. """
        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.draw(self.__data)
        ac.glColor4f(*Colors.white)

    def resize(self, resolution):
        """ Resizes the window. """
        mult = BoxComponent.resolution_map[resolution]
        ac.setSize(self.__window_id, 512 * mult, 85 * mult)
        ac.setText(self.__bt_resolution, resolution)
        for component in self.__components:
            component.resize(resolution)

    def set_active(self, active):
        """ Toggles the window status. """
        self.__active = active

    def update(self):
        """ Updates the engine information. """
        self.__data.update(self.__info)
        for component in self.__components:
            ac.glColor4f(*Colors.white)
            component.update(self.__data)
