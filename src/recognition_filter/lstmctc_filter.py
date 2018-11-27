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


class LstmctcFiter(Filter):

    def __init__(self, params, logger):
        assert(isinstance(params, dict))

        self.confident_thr = 0.8
        if 'confident_thr' in params:
            self.confident_thr = float(params['confident_thr'])
        self.root_dir = params['root_dir']

        self.proc_field_str = params['proc_field_keys']
        self.save_field_str = params['save_field_keys']
        self.infer_script_file = params['infer_script_file']

        self.proc_field_keys = set([x for x in self.proc_field_str.split(';')])
        self.save_field_keys = set([x for x in self.save_field_str.split(';')])

        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        self.root_dir = os.path.abspath(self.root_dir)

        self.lstm_ctc_dir = os.path.join(self.root_dir, 'lstmctc_filter')
        if not os.path.isdir(self.lstm_ctc_dir):
            os.makedirs(self.lstm_ctc_dir)

        self.lstmctc_input_file = os.path.join(self.lstm_ctc_dir, 'lstm_src_file.list')
        self.lstmctc_otput_file = os.path.join(self.lstm_ctc_dir, 'lstm_dst_file.list')
        self.lstmctc_image_dir = os.path.join(self.lstm_ctc_dir, 'images')
        if not os.path.isdir(self.lstmctc_image_dir):
            os.makedirs(self.lstmctc_image_dir)

        self.infer_params = {}
        self.infer_params['--net'] = params['net']
        self.infer_params['--input_h'] = int(params['input_h'])
        self.infer_params['--input_c'] = int(params['input_c'])
        self.infer_params['--model'] = params['model']
        self.infer_params['--max_w'] = params['max_w']
        self.infer_params['--batch_size'] = params['batch_size']
        self.infer_params['--test_file_lst'] = self.lstmctc_input_file
        self.infer_params['--save_predict']  = self.lstmctc_otput_file

    def datamap_to_stdlstm(self, data_map):
        line_list = []
        for image_key in data_map:
            local_file = data_map[image_key]['local_file']
            if not os.path.isfile(local_file):
                continue

            image_file = local_file
            for label_key in data_map[image_key]:
                if label_key not in self.proc_field_keys:
                    continue

                types_list =  data_map[image_key][label_key]['types']
                points_list = data_map[image_key][label_key]['points']
                context_list = data_map[image_key][label_key]['contents']

                for index, points in enumerate(points_list):
                    xmin = min([point[0] for point in points])
                    ymin = min([point[1] for point in points])
                    xmax = max([point[0] for point in points])
                    ymax = max([point[1] for point in points])

                    text = context_list[index]
                    cord = ','.join([str(x) for x in [xmin,ymin,xmax,ymax]])

                    if text is None or len(text)==0:
                        continue
                    line_list.append(image_file + ' ' + text + ' ' + cord + '\n')

        ret_list = auglstm_to_stdlstm(line_list, self.lstmctc_image_dir, '_processId0')

        with open(self.lstmctc_input_file, 'w') as reader:
            for line in ret_list:
                std_line, uin_line = line
                reader.write(std_line.strip() + '\n')

    def run_filter(self, data_maps):
        assert(isinstance(data_maps, dict))

        self.datamap_to_stdlstm(data_maps)

        infer_step(self.infer_script_file, self.infer_params)

        extract_map = {}
        with open(self.lstmctc_otput_file, 'r') as reader:
            for line in reader:
                error = 0
                line_sp = line.strip().split(' ')
                if len(line_sp)<4:
                    error = 1
                elif line_sp[2]!=line_sp[3] and float(line_sp[1])>self.confident_thr:
                    error = 1
                image_key = line_sp[0].split('_processId')
                image_key = image_key.split('/')[-1]

                if image_key not in extract_map:
                    extract_map[image_key] = error
                else:
                    exit_flag = extract_map[image_key]
                    if exit_flag == 0:
                        extract_map[image_key] = error

        self.save_datamap = {}
        self.abad_datamap = {}
        for image_key in data_maps:
            if image_key in extract_map and extract_map[image_key] == 1:
                self.abad_datamap[image_key] = data_maps[image_key]
            else:
                self.save_datamap[image_key] = data_maps[image_key]

        return self.save_datamap

    def get_abandon(self):
        return self.abad_datamap

