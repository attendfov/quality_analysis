# _*_ coding:utf-8 _*_
import os
import sys
import cv2
import copy
import random
import numpy as np


if sys.version.startswith('2'):
    reload(sys)
    sys.setdefaultencoding('utf-8')

path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(path)
sys.path.append(os.path.abspath(os.path.join(path, '..')))


class BooststrapFiter(Filter):

    def __init__(self, params, logger):
        assert(isinstance(params, dict))

        self.confident_thr = 0.8
        if 'confident_thr' in params:
            self.confident_thr = float(params['confident_thr'])
        self.root_dir = params['root_dir']

        self.model_start_step = 0
        self.model_iter_count = 6
        self.data_append_tag = params['data_append_tag']
        self.train_augfile = params['train_augfile']
        self.proc_field_str = params['proc_field_keys']
        self.save_field_str = params['save_field_keys']
        self.model_iter_count = int(params['model_iter_count'])
        self.model_start_step = int(params['model_start_step'])
        self.train_script_file = params['train_script_file']
        self.infer_script_file = params['infer_script_file']

        self.proc_field_keys = set([x for x in self.proc_field_str.split(';')])
        self.save_field_keys = set([x for x in self.save_field_str.split(';')])

        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        self.root_dir = os.path.abspath(self.root_dir)

        self.booststrap_dir = os.path.join(self.root_dir, 'booststrap_filter')
        if not os.path.isdir(self.booststrap_dir):
            os.makedirs(self.booststrap_dir)


        self.train_params = {}
        self.train_params['--augmentation'] = 1 if 'augmentation' not in params else int(params['augmentation'])
        self.train_params['--decay_rate'] = 0.8 if 'decay_rate' not in params else float(params['decay_rate'])
        self.train_params['--decay_steps'] = 60000 if 'decay_steps' not in params else int(params['decay_steps'])
        self.train_params['--learning_rate'] = 0.001 if 'learning_rate' not in params else float(params['learning_rate'])

        self.train_params['--batch_size'] = int(params['batch_size'])
        self.infer_params['--net'] = params['net']
        self.infer_params['--input_h'] = int(params['input_h'])
        self.infer_params['--input_c'] = int(params['input_c'])
        self.train_params['--char_dict'] = params['char_dict']
        self.infer_params['--restore'] = params['restore']
        self.infer_params['--max_w'] = int(params['max_w'])

        self.infer_params = {}
        self.infer_params['--net'] = params['net']
        self.infer_params['--input_h'] = int(params['input_h'])
        self.infer_params['--input_c'] = int(params['input_c'])
        self.infer_params['--max_w'] = int(params['max_w'])
        self.infer_params['--char_dict'] = params['char_dict']
        self.infer_params['--batch_size'] = int(params['batch_size'])

        #self.infer_params['--model'] = params['model']
        #self.infer_params['--test_file_lst'] = self.lstmctc_input_file
        #self.infer_params['--save_predict']  = self.lstmctc_otput_file



    def booststrap_train(self, data_map):
       pass


    def iter_step(self, stepid, data_map):
        step_dir = os.path.join(self.booststrap_dir, "step{}".format(self.model_start_step))
        if not os.path.isdir(step_dir):
            os.makedirs(step_dir)

        infer_params = copy.deepcopy(self.infer_params)

        if stepid==0:
            test_uin_lstm_file = os.path.join(step_dir, 'test_uin_lstm_file')
            test_std_lstm_file = os.path.join(step_dir, 'test_std_lstm_file')
            infer_std_lstm_file = os.path.join(step_dir, 'infer')
            self.datamap_to_stdlstm(data_map, test_uin_lstm_file, test_std_lstm_file)

            infer_params['--model'] = params['restore']
            infer_params['--save_predict'] = infer_std_lstm_file
            infer_params['--test_file_lst'] = test_std_lstm_file

            infer_step(self.infer_script_file, infer_params)
            split_step(infer_std_lstm_file,
                       test_uin_lstm_file,
                       pre_train_file,
                       select_train_file,
                       select_test_file,
                       select_uin_file
                       )





        if infer_params

        train_list_file =
        infer_list_file =
        union_list_file =

        if stepid==0:

            split_step(infer_file,
                   unin_file,
                   pre_train_file,
                   select_train_file,
                   select_test_file,
                   select_uin_file
                   )

        for iter_step in range(self.model_start_step, self.model_start_step+self.model_iter_count):



        self.model_start_step

        if



    def datamap_to_stdlstm(self, data_map, uinlstm_file, stdlstm_file):
        line_list = []
        for image_key in data_map:
            local_file = data_map[image_key]['local_file']
            if not os.path.isfile(local_file):
                continue

            image_file = local_file
            for label_key in data_map[image_key]:
                if label_key not in self.proc_field_keys:
                    continue

                types_list = data_map[image_key][label_key]['types']
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

        std_writer = open(stdlstm_file, 'w')
        uin_writer = open(uinlstm_file, 'w')
        for line in ret_list:
            std_line, uin_line = line
            std_writer.write(std_line.strip() + '\n')
            uin_writer.write(uin_line.strip() + '\n')
        std_writer.close()
        uin_writer.close()


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

