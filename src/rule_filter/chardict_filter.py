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
sys.path.append(os.path.join(path, '..'))
sys.path.append(os.path.abspath(os.path.join(path, '..')))

from filter import *

class ChardictFilter(Filter):
    def __init__(self, params, logger):
        assert(isinstance(params, dict))

        self.char_dict_file = params['char_dict_file']
        self.proc_field_str = params['proc_field_keys']
        self.save_field_str = params['save_field_keys']

        self.bad_count_thr  = 0
        if 'bad_count_thr' in params:
            self.bad_count_thr = int(params['bad_count_thr'])

        if 'unk_char_keys' not in params:
            self.unk_char_str = '☠️;*'
        else:
            self.unk_char_str = params['unk_char_keys']

        self.unk_char_set = set([x for x in self.unk_char_str.split(';')])

        self.char_dict = {}
        self.unk_char_dict = {key:index for index, key in enumerate(self.unk_char_set)}

        if not os.path.isfile(self.char_dict_file):
            return

        with open(self.char_dict_file, 'r') as reader:
            for index, line in enumerate(reader):
                sp = line.strip().split(' ')
                self.char_dict[sp[0]] = index

        self.proc_field_keys = set([x for x in self.proc_field_str.split(';')])
        self.save_field_keys = set([x for x in self.save_field_str.split(';')])

    def run_filter(self, data_maps):
        assert(isinstance(data_maps, dict))

        if len(self.char_dict) == 0:
            return data_maps

        data_maps_new = {}
        for image_key in data_maps:
            for label_key in data_maps[image_key]:
                if label_key in self.save_field_keys or label_key in self.proc_field_keys:
                    if image_key not in data_maps_new:
                        data_maps_new[image_key] = {}
                    data_maps_new[image_key][label_key] = data_maps[image_key][label_key]

        data_maps = data_maps_new

        for image_key in data_maps:
            for label_key in data_maps[image_key]:
                if 'contents' not in data_maps[image_key][label_key]:
                    continue

                if 'chardict_info' not in data_maps[image_key][label_key]:
                    data_maps[image_key][label_key]['chardict_info'] = []

                for index,content in enumerate(data_maps[image_key][label_key]['contents']):
                    unk_count = 0
                    bad_count = 0
                    corr_count = 0

                    if content is None or len(content) == 0:
                        data_maps[image_key][label_key]['chardict_info'].append([unk_count, bad_count, corr_count])
                        continue

                    for char in content:
                        if char in self.char_dict:
                            corr_count = corr_count + 1
                        elif char in self.unk_char_set:
                            unk_count = unk_count + 1
                        else:
                            bad_count = bad_count + 1

                    data_maps[image_key][label_key]['chardict_info'].append([unk_count, bad_count, corr_count])

        # add dicision moudle to choose the data
        self.save_datamap = {}
        self.abad_datamap = {}
        for image_key in data_maps:
            save_field_map = {}
            for label_key in data_maps[image_key]:
                if label_key in self.save_field_keys:
                    save_field_map[label_key] = data_maps[image_key][label_key]
                    continue

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

                    if bad_count > self.bad_count_thr:
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

                    self.abad_datamap[image_key][label_key]['types'] = abad_types
                    self.abad_datamap[image_key][label_key]['points'] = abad_points
                    self.abad_datamap[image_key][label_key]['contents'] = abad_contents
                    self.abad_datamap[image_key][label_key]['chardict_info'] = abad_chardict_info

                if len(save_types) > 0:
                    if image_key not in self.save_datamap:
                        self.save_datamap[image_key] = {}
                    if label_key not in self.save_datamap[image_key]:
                        self.save_datamap[image_key][label_key] = {}

                    self.save_datamap[image_key][label_key]['types'] = save_types
                    self.save_datamap[image_key][label_key]['points'] = save_points
                    self.save_datamap[image_key][label_key]['contents'] = save_contents
                    self.save_datamap[image_key][label_key]['chardict_info'] = save_chardict_info

            if image_key in self.abad_datamap:
                for save_key in save_field_map:
                    self.abad_datamap[image_key][save_key] = save_field_map[save_key]

            if image_key in self.save_datamap:
                for save_key in save_field_map:
                    self.save_datamap[image_key][save_key] = save_field_map[save_key]

        return self.save_datamap

    def get_abandon(self):
        return self.abad_datamap







