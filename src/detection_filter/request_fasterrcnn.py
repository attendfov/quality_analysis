# _*_ coding:utf-8 _*_

import os
import sys
import cv2
import time
import numpy as np
from PIL import Image
import multiprocessing



class RequestFastercnn:
    def __init__(self, params, logger=None):
        assert(isinstance(params, dict))
        cognition_dir = params['cognition_dir']
        assert(os.path.isdir(cognition_dir))
        cognition_dir = os.path.abspath(cognition_dir)
        sys.path.append(cognition_dir)
        import cognition.framework as cf

        self.proc_count = params['process_count']
        self.save_file = params['save_file']
        self.restore_type = params['restore_type']
        self.restore_file = params['restore_file']
        assert (restore_type in ['request', 'file', 'merge'])

        self.first_request = True

        self.client = None
        if restore_type == 'request':
            client_url = params['client_url']
            client_timeout = 5000
            if 'timeout' in params:
                client_timeout = int(params['timeout'])

            self.client = cf.SlaveClient(client_url, client_timeout)

        self.data_map = None

        if self.restore_type == 'file':
            self.data_map = self.restore_from_file(self.restore_file)
            if not os.path.isfile(self.save_file):
                self.save_to_file(self, self.data_map, self.save_file)

    def fetch_detection(self, image_files):
        if self.restore_type == 'request' and self.first_request:
            self.first_request = False
            self.data_map = self.multi_request(self, image_files, process_count=self.proc_count)
            if not os.path.isfile(self.save_file):
                self.save_to_file(self, self.data_map, self.save_file)

        ret_datamap = {}
        for img_file in image_files:
            img_name = img_file.split('/')[-1]
            if img_name in self.data_map:
                ret_datamap[img_name] = self.data_map['img_name']

        return ret_datamap

    def save_to_file(self, data_map, save_file):
        with open(save_file, 'w') as writer:
            keys = list(data_map.keys())
            keys.sort()
            for image_key in keys:
                dict_map = data_map[image_key]
                json_dumps = json.dumps(dict_map, ensure_ascii=False)
                writer.write(json_dumps+'\n')

    def restore_from_file(self, restore_file):
        data_map = {}
        with open(restore_file, 'r') as reader:
            for index, line in enumerate(reader):
                loads_dict = json.loads(line.strip())
                image_name = loads_dict['image']
                data_map[image_name] = loads_dict
        return data_map

    def request(self, image_files):
        dict_map = {}
        for index, image_file in enumerate(image_files):
            try:
                assert(os.path.isfile(image_file))
                image = Image.open(image_file)
                image_name = image_file.split('/')[-1]
                params = {'Image_name': image_name}
                result = self.client.send([np.asarray(image), str(params)])

                result = result[0]
                result = result.replace("\'", '\"')

                loads_dict = json.loads(result)
                image_name = loads_dict['image']
                dict_map[image_name] = loads_dict
                time.sleep(0.1)
            except Exception as e:
                continue
        return dict_map

    def multi_request(self, image_files, process_count=3):

        solo = (len(image_files)+process_count)/process_count + 1
        pool = multiprocessing.pool(processes=process_count)

        results = []
        for i in range(process_count):
            file_list = image_files[i*solo:(i+1)*solo]
            result = pool.apply_async(self.request, args=(file_list,))
            results.append(result)

        pool.close()
        pool.join()

        data_map = {}
        for result in results:
            result_map = result.get()
            for image_key in result_map:
                data_map[image_key] = result_map[image_key]

        return data_map















