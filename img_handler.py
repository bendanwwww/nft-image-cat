# -*- coding:utf-8 -*-

import os
import sys
import random
import uuid
import argparse
import itertools
from PIL import Image 

class img_handler(object):
    # 组件目录
    component_path = ''
    # 图片输出目录
    img_output_path = ''
    # 图片宽度
    img_wigth = 0
    # 图片长度
    img_high = 0
    # 组件种类
    component_type_list = []
    # 组件文件
    component_file_list = []
    # 图片数量
    img_number = 0
    # 目录下所有组件类型
    component_dir_list = []
    # 组件类型下所有组件
    component_dict = {}
    # 组件全路径
    component_path_dict = {}

    def __init__(self, args):
        self.component_path = args.path
        self.img_output_path = args.out
        self.img_wigth = args.wigth
        self.img_high = args.high
        self.img_number = int(args.number)
        self.component_type_list = args.type.replace(' ', '').split(',')
        # 创建输出文件夹
        folder = os.path.exists(self.img_output_path)
        if not folder:
            os.makedirs(self.img_output_path)
        # 遍历组件目录下所有文件夹
        self.get_all_component(self.component_path)
        # 若指定组件文件则按指定组装
        if args.component != 'all':
            self.component_file_list = args.component.replace(' ', '').split(',')

    # 执行逻辑
    def run(self):
        # 若有指定文件 则直接执行
        if len(self.component_file_list) > 0:
            self.handler(self.img_output_path, self.build_file_name(), self.component_file_list)
            return
        # 计算最大随机数
        max_random_number = 1
        for type in self.component_type_list:
            if type not in self.component_dict:
                print('未找到传入组件类型 ' + type)
                return
            max_random_number *= len(self.component_dict[type])
        build_number = min(self.img_number, max_random_number)
        # 随机组件
        build_component_list = self.random_component(self.component_type_list, build_number, max_random_number)
        # 生成图片
        index = 0
        for component_list in build_component_list:
            print('共' + str(len(build_component_list)) + '张图片 正在生成第' + str(index + 1) + '张')
            self.handler(self.img_output_path, self.build_file_name(), component_list)
            index += 1

    # 生成图片文件名
    def build_file_name(self):
        return uuid.uuid1().__str__()

    # 随机组件
    def random_component(self, component_append_type, build_number, max_build_number):
        # 如果需构造图片超过最大构造数的一半 则使用全随机算法
        if build_number * 2 > max_build_number:
            return self.random_all(component_append_type, build_number)
        else:
            return self.random_weight(component_append_type, build_number, max_build_number)

    # 全随机算法
    def random_all(self, component_append_type, build_number):
        all_component_list = []
        for component_type in component_append_type:
            all_component_list.append(self.component_dict[component_type])
        all_permutations = list(itertools.product(*all_component_list))
        return random.sample(all_permutations, build_number)
        
    # 权重随机算法
    def random_weight(self, component_append_type, build_number, max_build_number):
        # 组件列表
        build_component_list = []
        # 组件字符串列表 用于计算已经存在的组合
        build_component_str_list = []
        # 计算每个组件最多被使用几次 生成组件随机概率
        component_weights_dict = {}
        for component_type in component_append_type:
            type_max_use_number = int(max_build_number / len(self.component_dict[component_type]))
            type_weights = [type_max_use_number for _ in range(len(self.component_dict[component_type]))]
            component_weights_dict[component_type] = type_weights
        while len(build_component_list) < build_number:
            # print(str(len(build_component_list)))
            component_list = []
            component_index_dict = {}
            for component_type in component_append_type:
                choices_img = random.choices(self.component_dict[component_type], component_weights_dict[component_type])[0]
                component_list.append(choices_img)
                component_index_dict[component_type] = self.component_dict[component_type].index(choices_img)
            # 判断组合是否已存在
            if ','.join('%s' %c for c in component_list) in build_component_str_list:
                continue
            # 加入组件列表
            build_component_list.append(component_list)
            build_component_str_list.append(','.join('%s' %c for c in component_list))
            # 调整概率
            for component_type in component_index_dict:
                component_weights_dict[component_type][component_index_dict[component_type]] -= 1
        return build_component_list


    # 获取目录下所有组件
    def get_all_component(self, path):
        path_file = os.listdir(path)
        for p in path_file:
            if os.path.isdir(path + '/' + p):
                self.component_dir_list.append(p)
        for d in self.component_dir_list:
            component_file_list = os.listdir(path + '/' + d)
            self.component_dict[d] = component_file_list
            for c in component_file_list:
                self.component_path_dict[c] = path + '/' + d + '/' + c

    # 组装图片
    def handler(self, file_path, file_name, images):
        if len(images) < 2:
            return
        last = None
        for item in images:
            img_path = self.component_path_dict[item]
            img = Image.open(img_path)
            img = img.resize((self.img_high, self.img_wigth), Image.ANTIALIAS)
            if last is None:
                last = img.convert('RGBA')
            else:
                last = Image.alpha_composite(last, img.convert('RGBA'))
        rgb_im = last.convert('RGB')
        rgb_im.save(file_path + '/' + file_name + ".png")

# 获取当前路径
code_path = os.path.abspath(os.path.dirname(__file__))
# 获取命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--path', '-p', help='组件目录 不传默认为当前目录下images文件夹', default=code_path + '/images')
parser.add_argument('--type', '-t', help='需要组装的组件种类, 多个类型逗号隔开, 图层顺序以传入顺序为准, 传入种类需和组件目录下组件文件夹名一致 必传参数', required=True)
parser.add_argument('--component', '-c', help='指定组件拼装, 多张组件逗号隔开, 图层顺序以传入顺序为准, 传入组件需和组件文件名一致 不传默认随机组装组件种类下的组件', default='all')
parser.add_argument('--wigth', '-w', help='图片宽度 不传默认500px', default=500)
parser.add_argument('--high', '-h', help='图片长度 不传默认500px', default=500)
parser.add_argument('--out', '-o', help='图片输出目录 不传默认为当前目录下out文件夹', default=code_path + '/out')
parser.add_argument('--number', '-n', help='组装组件数量, 当未指定组件拼装时起效', default=sys.maxsize)
args = parser.parse_args()

if __name__ == '__main__':
    # try:
    #     handler = img_handler(args)
    #     handler.run()
    # except Exception as e:
    #     print(e)
    handler = img_handler(args)
    handler.run()