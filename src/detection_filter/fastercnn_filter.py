# _*_ coding:utf-8 _*_
import os
import sys
import cv2
import random
import numpy as np


if sys.version.startswith('2'):
    reload(sys)
    sys.setdefaultencoding('utf-8')

path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(path)
sys.path.append(os.path.abspath(os.path.join(path, '..')))

from utils import *
from filter import *
from request_fasterrcnn import *

class FastercnnFiter(Filter):
    def __init__(self, params, logger):
        assert(isinstance(params, dict))

        self.proc_field_str = params['proc_field_keys']
        self.save_field_str = params['save_field_keys']
        self.bad_iou_thr = 0.35
        if 'bad_iou_thr' in params:
            self.bad_iou_thr = float(params['bad_iou_thr'])

        self.field_name_map = {}

        self.save_field_keys = set([x for x in self.save_field_str.split(';')])

        request_inst = RequestFastercnn(params, logger)
        self.detect_list = [[xmin,ymin,xmax,ymax,label]]

    def detect_match(self, bbox, detect_list):
        max_iou = 0.0
        max_lbl = ''
        for detect_line in detect_list:
            xmin,ymin,xmax,ymax,label = detect_line
            iou_value = iou(bbox, [xmin,ymin,xmax,ymax])
            if iou_value>max_iou:
                max_iou = iou_value
                max_lbl = label
        return max_iou,max_lbl

    def run_filter(self, data_maps):
        assert(isinstance(data_maps, dict))

        self.save_datamap = {}
        self.abad_datamap = {}
        for image_key in data_maps:
            save_field_map = {}
            for label_key in data_maps[image_key]:
                if label_key in self.save_field_keys:
                    save_field_map[label_key] = data_maps[image_key][label_key]
                    continue

                types = data_maps[image_key][label_key]['types']
                points = data_maps[image_key][label_key]['points']
                contents = data_maps[image_key][label_key]['contents']

                umatch = False

                for index,content in enumerate(contents):
                    bbox_points = points[index]
                    xmin = min([int(point[0]) for point in bbox_points])
                    ymin = min([int(point[1]) for point in bbox_points])
                    xmax = min([int(point[0]) for point in bbox_points])
                    ymax = max([int(point[1]) for point in bbox_points])

                    bbox = [xmin,ymin,xmax,ymax]
                    max_iou, max_lbl = self.detect_match(bbox, self.detect_list)
                    if max_lbl in  self.field_name_map:
                        max_lbl = self.field_name_mapp[max_lbl]
                    if max_iou>self.bad_iou_thr and label_key!=max_lbl:
                        umatch = True
                    if umatch:
                        break

                if umatch:
                    if image_key not in self.save_datamap:
                        self.save_datamap[image_key] = {}
                    if label_key not in self.save_datamap[image_key]:
                        self.save_datamap[image_key][label_key] = {}

                    self.save_datamap[image_key][label_key]['types'] = types
                    self.save_datamap[image_key][label_key]['points'] = points
                    self.save_datamap[image_key][label_key]['contents'] = contents
                else:
                    if image_key not in self.abad_datamap:
                        self.abad_datamap[image_key] = {}
                    if label_key not in self.abad_datamap[image_key]:
                        self.abad_datamap[image_key][label_key] = {}

                    self.abad_datamap[image_key][label_key]['types'] = types
                    self.abad_datamap[image_key][label_key]['points'] = points
                    self.abad_datamap[image_key][label_key]['contents'] = contents

            if image_key in self.abad_datamap:
                for save_key in save_field_map:
                    self.abad_datamap[image_key][save_key] = save_field_map[save_key]

            if image_key in self.save_datamap:
                for save_key in save_field_map:
                    self.save_datamap[image_key][save_key] = save_field_map[save_key]

        return self.save_datamap

    def get_abandon(self):
        return self.abad_datamap

