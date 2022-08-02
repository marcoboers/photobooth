#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

from PIL import Image

import requests
import cv2
from .CameraInterface import CameraInterface


class CameraSonyAlpha(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        logging.info('Using OpenCV for Sony Alpha camera integration')

        opencv_url = self._cfg.get('Camera', 'opencv_url')

        logging.info('Sony opencv_url is set to ' + opencv_url)

        # Connect to camera
        logging.info("Connecting to camera...")
        payload = {"version": "1.0", "id": 1, "method": "startRecMode", "params": []}
        r = requests.post(opencv_url, json=payload)
        if r.status_code != 200:
            logging.info("Could not connect to camera: " + str(r.status_code))
            exit()
        logging.info("Response: " + str(r.json()))

        # Request preview stream
        logging.info("Requesting medium res preview stream...")
        # payload = {"version": "1.0", "id": 1, "method": "startLiveviewWithSize", "params": ["M"]}
        payload = {"version": "1.0", "id": 1, "method": "startLiveview", "params": []}
        r = requests.post(opencv_url, json=payload)
        response = r.json()
        logging.info("Response: " + str(response))
        url = response["result"][0]
        logging.info("URL: " + str(url))

        self._cap = cv2.VideoCapture(url)

    def setActive(self):

        if not self._cap.isOpened():
            self._cap.open(0)
            if not self._cap.isOpened():
                raise RuntimeError('Camera could not be opened')

    def setIdle(self):

        if self._cap.isOpened():
            self._cap.release()

    def getPreview(self):

        return self.getPicture()

    def getPicture(self):

        self.setActive()
        status, frame = self._cap.read()
        if not status:
            raise RuntimeError('Failed to capture picture')

        # OpenCV yields frames in BGR format, conversion to RGB necessary.
        # (See https://stackoverflow.com/a/32270308)
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
