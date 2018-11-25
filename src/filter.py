# _*_ coding:utf-8 _*_

import os
import sys
import cv2

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty


class Filter:
    def __init__(self, params, logger):
        pass


    @abstractmethod
    def run_filter(self, data_maps):
        return data_maps


    @abstractmethod
    def get_abandon(self):
        pass








