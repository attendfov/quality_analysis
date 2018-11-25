# _*_ coding:utf-8 _*_

import os
import sys
import numpy as np


def gene_data():
    data_map = {}

    data_map['1.jpg'] = {}
    data_map['1.jpg']['name'] = {}
    points = [[[0,0],[1,1],[2,2],[3,3]], [[4,4],[5,5],[6,6],[7,7]]]
    types = [0, 1]
    contents = ['张三', '李四']

    data_map['1.jpg']['name']['points'] = points
    data_map['1.jpg']['name']['types'] = types
    data_map['1.jpg']['name']['contents'] = contents

    points = [[[0, 0], [1, 1], [2, 2], [3, 3]], [[4, 4], [5, 5], [6, 6], [7, 7]]]
    types = [0, 1]
    contents = ['KD123', 'UC256']
    data_map['1.jpg']['id'] = {}
    data_map['1.jpg']['id']['points'] = points
    data_map['1.jpg']['id']['types'] = types
    data_map['1.jpg']['id']['contents'] = contents
    data_map['1.jpg']['local_file'] = '/home/admin/1.jpg'

    return data_map


if __name__=='__main__':
    data_map = gene_data()
    print(data_map)




