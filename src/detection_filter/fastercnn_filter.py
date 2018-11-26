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

        request_inst = RequestFastercnn(params, logger)

        self.detect_list = [[xmin,ymin,xmax,ymax,label]]


    def detect_match(self, bbox, detect_list):


    def run_filter(self, data_maps):
        assert(isinstance(data_maps, dict))

        self.save_datamap = {}
        self.abad_datamap = {}
        for image_key in data_maps:
            for label_key in data_maps[image_key]:
                save_types = []
                save_points = []
                save_contents = []

                abad_types = []
                abad_points = []
                abad_contents = []

                types = data_maps[image_key][label_key]['types']
                points = data_maps[image_key][label_key]['points']
                contents = data_maps[image_key][label_key]['contents']

                for
        

        
        for image_key in data_maps:
            for label_key in data_maps[image_key]:
                save_types = []
                save_points = []
                save_contents = []
                save_chardict_info = []

                abad_types = []
                abad_points = []
                abad_contents = []
                abad_chardict_info = []

                types = data_maps[image_key][label_key]['types']
                points = data_maps[image_key][label_key]['points']
                contents = data_maps[image_key][label_key]['contents']
                chardict_info = data_maps[image_key][label_key]['chardict_info']
                for index, info in enumerate(chardict_info):
                    unk_count, bad_count, corr_count = info

                    if bad_count > 0:
                        abad_types.append(types[index])
                        abad_points.append(points[index])
                        abad_contents.append(contents[index])
                        abad_chardict_info.append(chardict_info[index])
                    else:
                        save_types.append(types[index])
                        save_points.append(points[index])
                        save_contents.append(contents[index])
                        save_chardict_info.append(chardict_info[index])

                if len(abad_types)>0:
                    if image_key not in self.abad_datamap:
                        self.abad_datamap[image_key] = {}
                    if label_key not in self.abad_datamap[image_key]:
                        self.abad_datamap[image_key][label_key] = {}

                    self.abad_datamap[image_key][label_key]['types'] = save_types
                    self.abad_datamap[image_key][label_key]['points'] = save_points
                    self.abad_datamap[image_key][label_key]['contents'] = save_contents
                    self.abad_datamap[image_key][label_key]['chardict_info'] = save_chardict_info

                if len(save_types)>0:
                    if image_key not in self.save_datamap:
                        self.save_datamap[image_key] = {}
                    if label_key not in self.save_datamap[image_key]:
                        self.save_datamap[image_key][label_key] = {}

                    self.save_datamap[image_key][label_key]['types'] = save_types
                    self.save_datamap[image_key][label_key]['points'] = save_points
                    self.save_datamap[image_key][label_key]['contents'] = save_contents
                    self.save_datamap[image_key][label_key]['chardict_info'] = save_chardict_info

        return save_datamap

    def get_abandon(self):
        return self.abad_datamap
