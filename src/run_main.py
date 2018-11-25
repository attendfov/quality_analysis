# _*_ coding:utf-8 _*_
import os
import sys
import cv2
import random
import numpy as np


if sys.version.startswith('2'):
    reload(sys)
    sys.setdefaultencoding('utf-8')

abspath = os.path.dirname(os.path.realpath(__file__))

sys.path.append(abspath)
print(os.path.join(abspath, 'rule_filter'))
sys.path.append(os.path.join(abspath, 'rule_filter'))

from gene_data import *
from chardict_filter import *


def test_chardict_filter():
    data_map = gene_data()
    print ('origin data:', data_map)

    params = {}
    params['char_dict_file'] = 'id_char.dict'
    params['proc_field_keys'] = 'name'
    params['save_field_keys'] = 'local_file'
    params['bad_count_thr'] = '0'

    dict_fileter = ChardictFilter(params, None)
    data_map = dict_fileter.run_filter(data_map)
    abad_map = dict_fileter.get_abandon()

    print('save_data', data_map)
    print('abad_data', abad_map)


if __name__=='__main__':
    test_chardict_filter()









