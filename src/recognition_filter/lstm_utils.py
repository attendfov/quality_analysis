# _*_ coding:utf-8 _*_

import os
import sys
import cv2
import random
import numpy as np
import multiprocessing
import multiprocessing as mp


if sys.version.startswith('2'):
    import subprocess as sub_commands
elif sys.version.startswith('3'):
    import  commands  as sub_commands


def auglstm_to_stdlstm(src_list, save_dir, posfix):
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    abspath = os.path.abspath(save_dir)
    params = [cv2.IMWRITE_JPEG_QUALITY, 100]

    ret_list = []
    for index, line in  enumerate(src_list):
        try:
            line_sp = line.strip().split(' ')
            if len(line_sp) != 3:
                continue

            img_file = line_sp[0]
            img_text = line_sp[1]
            img_cord = line_sp[2]

            if img_text is None or len(img_text)==0:
                continue

            if not os.path.isfile(img_file):
                continue

            xmin,ymin,xmax,ymax = [int(x) for x in img_cord.split(',')]
            image = cv2.imread(img_file)
            imgh,imgw = image.shape[:2]
            xmin = min(imgw, max(0, xmin))
            xmax = min(imgw, max(0, xmax))
            ymin = min(imgh, max(0, ymin))
            ymax = min(imgh, max(0, ymax))

            image = image[ymin:ymax, xmin:xmax]
            image_name = os.path.basename(img_file)
            image_name = image_name + '_' + posfix + str(index) + '_' + '.jpg'
            saved_name = os.path.join(abspath, image_name)
            cv2.imwrite(saved_name, image, params)
            std_line = saved_name + ' ' + img_text
            aug_line = line.strip()
            ret_list.apppend([std_line, aug_line + ' ' + std_line])
        except Exception as e:
            print('auglstm_to_stdlstm Exceptaion:', e)

        return ret_list


def multi_auglstm_to_stdlstm(src_file, stdlstm_file, uinlstm_file, save_dir, cpu_count=mp.cpu_count()*2):
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    assert(os.path.isfile(src_file))

    writer_stdlstm = open(stdlstm_file, 'w')
    writer_uinlstm = open(uinlstm_file, 'w')


    reader = open(src_file, 'r')
    lines = reader.readlines()
    line_count = len(lines)
    reader.close()

    solo_size = int((line_count+cpu_count)/cpu_count+1)

    results = []
    for i in range(cpu_count):
        proc_list = lines[i*solo_size:(i+1)*solo_size]
        result = pool.apply_async(auglstm_to_stdlstm, (proc_list, save_dir, 'procId{}'.format(i)))
        results.append(result)
    pool.close()
    pool.join()

    for result in results:
        for line_list in result.get():
            writer_stdlstm.write(line_list[0] + '\n')
            writer_uinlstm.write(line_list[1] + '\n')

    writer_stdlstm.close()
    writer_uinlstm.close()


def train_step(train_script_file, train_params):

    assert('model_dir' in train_params)
    assert('model_name' in train_params)
    assert('test_file' in train_params)
    assert('train_file' in train_params)
    assert('char_dict' in train_params)
    assert (os.path.isfile(train_script_file))

    if 'train_log' not in train_params:
        train_params['train_log'] = 'train_log'

    run_code = ''
    for key in train_params:
        run_code = ' ' + str(key) + ' ' + train_params[key]

    run_code = 'sudo sh ' + train_script_file + run_code
    print('run_train_code:', run_code)
    sub_commands.getstatusoutput(run_code)


def infer_step(test_script_file, test_params):
    assert(os.path.isfile(test_script_file))

    run_code = ''
    for key in test_params:
        run_code = ' ' + str(key) + ' ' + test_params[key]

    run_code = 'sudo sh ' + str(test_script_file) + run_code
    print('run_infer_code:', run_code)
    sub_commands.getstatusoutput(run_code)


def selec_imagekey_form_dataline(line):
    #image_file, score, inf_txt, grt_txt
    line_sp = line.split(' ')
    if len(line_sp) < 4:
        return line_sp[0]

    image_file, score, inf_txt, grt_txt = line.strip().split('')

    if inf_txt!=grt_txt:
        return line_sp[0]


def split_step(infer_file,
               unin_file,
               pre_train_file,
               select_train_file,
               select_test_file,
               select_uin_file,
               select_func=selec_imagekey_form_dataline):
    assert(os.path.isfile(infer_file))
    assert(os.path.isfile(unin_file))

    train_list = []
    if pre_train_file is not None and os.path.isfile(pre_train_file):
        with open(pre_train_file, 'r') as reader:
            for index, line in enumerate(reader):
                train_list.append(line.strip())


    corr_train_keys = []
    error_test_keys = []

    for line in open(infer_file, 'r'):
        line_sp = line.strip().split(' ')
        if len(line_sp) < 4:
            error_test_keys.append(line_sp[0])
        elif line_sp[2]==line_sp[3] and float(sp[1])>0.8:
            corr_train_keys.append(line_sp[0])
        else:
            error_test_keys.append(line_sp[0])

    corr_train_keys = set(corr_train_keys)
    error_test_keys = set(error_test_keys)

    print("corr_train_keys size:", len(corr_train_keys))
    print("error_test_keys size:", len(error_test_keys))

    corr_train_list = []
    error_test_list = []
    error_unin_list = []
    for line in open(unin_file, 'r'):
        sp = line.strip().split(' ')
        image_key = sp[3]

        if image_key in corr_train_keys:
            corr_train_list.append(' '.join(sp[:3]))
        elif image_key in error_test_keys:
            error_test_list.append(' '.join(sp[3:]))
            error_unin_list.append(line.strip())

    corr_train_list = train_list + corr_train_list

    with open(select_train_file, 'w') as reader:
        for line in corr_train_list:
            reader.write(line.strip() + '\n')

    with open(select_test_file, 'w') as reader:
        for line in error_test_list:
            reader.write(line.strip() + '\n')

    with open(select_uin_file, 'w') as reader:
        for line in error_unin_list:
            reader.write(line.strip() + '\n')










