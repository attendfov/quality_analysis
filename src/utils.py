# _*_ coding:utf-8 _*_
import os
import sys
import cv2
import random
import numpy as np


def iou(bbox1, bbox2):
    xmin1,ymin1,xmax1,ymax1 = bbox1[:4]
    xmin2,ymin2,xmax2,ymax2 = bbox2[:4]

    if xmin1>=xmax2 or xmin2>=xmax1:
        return 0.0
    if ymin1>=ymax2 or ymin2>=ymax1:
        return 0.0

    area1 = (xmax1-xmin1)*(ymax1-ymin1)
    area2 = (xmax2-xmin2)*(ymax2-ymin2)

    insect_xmin = max(xmin1,xmin2)
    insect_ymin = max(ymin1,ymin2)
    insect_xmax = min(xmax1,xmax2)
    insect_ymax = min(ymax1,ymax2)

    insect_area = (insect_xmax-insect_xmin)*(insect_ymax-insect_ymin)

    return  insect_area/(area1+area2-insect_area+0.0000001)


def iou_test():

    bbox1 = [10,10,20,20]
    bbox2 = [10,10,20,20]

    print(iou(bbox1, bbox2))

def load_class(name):
    split_list = name.split('.')
    import_module = __import__(split_list[0])
    for comp in  split_list[1:]:
        mod = getattr(import_module, comp)
    return mod




class JsonReader:
    pass



if __name__=='__main__':
    iou_test()








#    data_map
#       |
#       |
#       v
#    rule_filter
#       |
#       |
#       v
#    detection_filter
#       |
#       |
#       v
#    recognitiion_filter








