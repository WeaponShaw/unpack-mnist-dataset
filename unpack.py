#!/usr/bin/env ipython

import os
import sys
import struct
import PIL.Image as Image


def check_dir(dir_path):
    if os.path.isdir(dir_path) == False:
        os.system('mkdir -p %s' % dir_path)


def check_file(file_name, url):
    if os.path.isfile('mnist_data/%s' % file_name) == False:
        os.chdir('mnist_data')
        os.system('wget -O %s.gz \'%s\'' % (file_name, url))
        os.system('gunzip %s.gz' % (file_name))
        os.chdir('..')


def binary_2_int(b):
    i = bytearray(b)
    i[0] = b[3]
    i[1] = b[2]
    i[2] = b[1]
    i[3] = b[0]
    return struct.unpack('i', i)[0]


class Labels(object):
    def __init__(self, label_file):
        self.label_f = open(label_file, 'rb')
        msb = self.label_f.read(4)
        msb = binary_2_int(msb)
        if msb != 2049:
            raise Exception('wrong label msb')

        cnt = self.label_f.read(4)
        self.cnt = binary_2_int(cnt)
        if self.cnt <= 0:
            raise Exception('label cnt less then 0')

        self.cur_idx = 0

    def __iter__(self, ):
        return self

    def next(self, ):
        if self.cur_idx >= self.cnt:
            raise StopIteration()
        else:
            self.cur_idx += 1
            label = ord(self.label_f.read(1))
            return label


class Images(object):
    def __init__(self, data_file):
        self.data_f = open(data_file, 'rb')
        msb = self.data_f.read(4)
        msb = binary_2_int(msb)
        if msb != 2051:
            raise Exception('wrong data msb')

        cnt = self.data_f.read(4)
        self.cnt = binary_2_int(cnt)
        if self.cnt <= 0:
            raise Exception('label cnt less then 0')

        row_cnt = self.data_f.read(4)
        self.row_cnt = binary_2_int(row_cnt)
        if self.row_cnt <= 0:
            raise Exception('row cnt less then 0')

        col_cnt = self.data_f.read(4)
        self.col_cnt = binary_2_int(col_cnt)
        if self.col_cnt <= 0:
            raise Exception('col cnt less then 0')

        self.cur_idx = 0

    def __iter__(self, ):
        return self

    def next(self, ):
        if self.cur_idx >= self.cnt:
            raise StopIteration()
        else:
            self.cur_idx += 1
            raw_bytes = self.data_f.read(self.row_cnt * self.col_cnt)
            img = Image.frombytes('L', (self.row_cnt, self.col_cnt), raw_bytes)
            return img


def unpack(label_file, data_file, out_dir):
    check_dir(out_dir)
    labels = Labels(label_file)
    images = Images(data_file)
    if labels.cnt != images.cnt:
        raise Exception('labels cnt is not equal images cnt')
    idx = 0
    for label, img in zip(labels, images):
        idx += 1
        img.save('%s/%d_%d.jpg' % (out_dir, idx, label))
        if idx % 1000 == 0:
            print idx


def get_data():
    check_dir('mnist_data')
    check_file('train-images-idx3-ubyte', 'http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz')
    check_file('train-labels-idx1-ubyte', 'http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz')
    check_file('t10k-images-idx3-ubyte', 'http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz')
    check_file('t10k-labels-idx1-ubyte', 'http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz')


def main():
    get_data()
    unpack('./mnist_data/train-labels-idx1-ubyte', './mnist_data/train-images-idx3-ubyte', './images/train')
    unpack('./mnist_data/t10k-labels-idx1-ubyte', './mnist_data/t10k-images-idx3-ubyte', './images/test')


if __name__ == '__main__':
    main()
