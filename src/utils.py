# _*_ coding:utf-8 _*_
import os
import sys
import cv2
import random
import numpy as np



def load_class(name):
    split_list = name.split('.')
    import_module = __import__(split_list[0])
    for comp in  split_list[1:]:
        mod = getattr(import_module, comp)
    return mod





class JsonReader:
    pass







    data_map
       |
       |
       v
    rule_filter
       |
       |
       v
    detection_filter
       |
       |
       v
    recognitiion_filter








