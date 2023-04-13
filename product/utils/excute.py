# -*- coding: utf-8 -*-
import re
import json
import copy

el_exp = r"\$\{(.+?)\}"
pattern = re.compile(el_exp)
fields = ['headers', 'url', 'params']


class Execute(object):
    def __init__(self):
        self.value_list = []
        self.key_list = []

    # 替换内容中的变量, 返回字符串型
    def replace_var(self, content, var_name, var_value):
        if not isinstance(content, str):
            content = json.dumps(content)
        var_name = "${" + var_name + "}"
        content = content.replace(str(var_name), str(var_value))
        return content

    # 从内容中提取所有变量名, 变量格式为${variable},返回变量名list
    def extract_variables(self, content):
        variable_regexp = r"\$\{(.+?)\}"
        if not isinstance(content, str):
            content = str(content)
        try:
            return re.findall(variable_regexp, content)
        except TypeError:
            return []

    # 在内容中获取某一参数的值
    def get_param(self, param, content):
        param_val = None
        if isinstance(content, str):
            # content = json.loads(content)
            try:
                content = json.loads(content)
            except:
                content = ""
        if isinstance(content, dict):
            param_val = self.get_param_reponse(param, content)
        if isinstance(content, list):
            dict_data = {}
            for i in range(len(content)):
                try:
                    dict_data[str(i)] = eval(content[i])
                except:
                    dict_data[str(i)] = content[i]
            param_val = self.get_param_reponse(param, dict_data)
        if param_val is None:
            return param_val
        else:
            if "$" + param == param_val:
                param_val = None
            return param_val

    def get_param_reponse(self, param_name, dict_data, default=None):
        for k, v in dict_data.items():
            if k == param_name:
                return v
            else:
                if isinstance(v, dict):
                    ret = self.get_param_reponse(param_name, v)
                    if ret is not default:
                        return ret
                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            ret = self.get_param_reponse(param_name, i)
                            if ret is not default:
                                return ret
                        else:
                            pass
        return default

    def get_dict_all(self, dict_data):
        """
        多维/嵌套字典数据无限遍历，获取json返回结果的所有key/value值集合
        :param dict_data:
        :return: value_list
        """
        if isinstance(dict_data, dict):  # 使用isinstance检测数据类型
            for x in range(len(dict_data)):
                temp_key = list(dict_data.keys())[x]
                temp_value = dict_data[temp_key]
                if isinstance(temp_value, dict):
                    self.get_dict_all(temp_value)
                elif isinstance(temp_value, list):
                    self.get_dict_all(temp_value)
                else:
                    self.value_list.append(temp_value)
        elif isinstance(dict_data, list):
            for k in dict_data:
                if isinstance(k, dict):
                    for x in range(len(k)):
                        temp_key = list(k.keys())[x]
                        temp_value = k[temp_key]
                        if isinstance(temp_value, dict):
                            self.get_dict_all(temp_value)
                        elif isinstance(temp_value, list):
                            self.get_dict_all(temp_value)
                        else:
                            self.value_list.append(temp_value)
        return self.value_list

    def get_dict_all_keys(self, dict_data):
        """
        多维/嵌套字典数据无限遍历，获取json返回结果的所有key/value值集合
        :param dict_data:
        :return: key_list
        """
        if isinstance(dict_data, dict):  # 使用isinstance检测数据类型
            for x in range(len(dict_data)):
                temp_key = list(dict_data.keys())[x]
                temp_value = dict_data[temp_key]
                self.key_list.append(temp_key)
                self.get_dict_all_keys(temp_value)  # 自我调用实现无限遍历
        elif isinstance(dict_data, list):
            for k in dict_data:
                if isinstance(k, dict):
                    for x in range(len(k)):
                        temp_key = list(k.keys())[x]
                        temp_value = k[temp_key]
                        self.key_list.append(temp_key)
                        self.get_dict_all_keys(temp_value)
        return self.key_list


class FindPath(object):
    def __init__(self, target):
        self.target = target

    def find_the_value(self, target, value, path='', path_list=[]):
        '''完全匹配，每经过一层(list、dict)都会记录path，到了最后一层且当前target就是要找的目标，才把对应的path记录下来
        :param target: 被搜索的目标
        :param value: 要搜索的关键字
        :param path: 当前所在的路径
        :param path_list: 存放所有path的列表
        判断当前target类型：···是字典，循环内容，每个键值都记录下路径path，然后以当前值v为判断target，调用自身传入添加了的path判断
                             ···是列表，循环内容，每个元素都记录下路径path，然后以当前元素为判断target，调用自身传入添加了的path判断
                             ···是str或者int，那么就判断当前target是否就是要搜索的value，如果是，那就把路径path放进list里面'''
        if isinstance(target, dict):
            for k, v in target.items():
                path1 = copy.deepcopy(path)
                path1 = path1 + str([k])
                self.find_the_value(v, value, path1, path_list)

        elif isinstance(target, (list, tuple)):  # 判断了它是列表
            for i in target:
                path1 = copy.deepcopy(path)
                posi = target.index(i)
                path1 = path1 + '[%s]' % posi
                self.find_the_value(i, value, path1, path_list)

        elif isinstance(target, (str, int)):
            if str(value) == str(target):  # 必须完全相同
                path_list.append(path)

    def find_in_value(self, target, value, path='', path_list=[]):
        if isinstance(target, dict):
            for k, v in target.items():
                path1 = copy.deepcopy(path)
                path1 = path1 + str([k])
                self.find_in_value(v, value, path1, path_list)

        elif isinstance(target, (list, tuple)):  # 判断了它是列表
            for i in target:
                path1 = copy.deepcopy(path)
                posi = target.index(i)
                path1 = path1 + '[%s]' % posi
                self.find_in_value(i, value, path1, path_list)

        elif isinstance(target, (str, int)):
            if str(value) in str(target):  #
                path_list.append(path)

    def find_the_key(self, target, key, path='', path_list=None):
        '''查找key，每经过一层(list、dict)都会记录path，在字典时，若当前的k就是要找的key，那就把对应的path记录下来
                :param target: 被搜索的目标
                :param key: 要搜的键
                :param path: 当前所在的路径
                :param path_list: 存放所有path的列表
                判断当前target类型：···是字典，循环内容，每个键值都记录下路径path，判断当前k是否要查找的：~~~是，那就把路径path放进list里面
                                                                                                 ~~~不是，以当前值v为判断target，调用自身传入添加了的path判断
                                  ···是列表，循环内容，每个元素都记录下路径path，然后以当前元素为判断target，调用自身传入添加了的path判断
        '''
        if isinstance(target, dict):
            for k, v in target.items():
                path1 = copy.deepcopy(path)
                path1 = path1 + str([k])
                if str(key) == str(k):
                    path_list.append(path1)
                else:
                    self.find_the_key(v, key, path1, path_list)

        elif isinstance(target, (list, tuple)):  # 判断了它是列表
            for i in target:
                path1 = copy.deepcopy(path)
                posi = target.index(i)
                path1 = path1 + '[%s]' % posi
                self.find_the_key(i, key, path1, path_list)

    # ====================================================================================

    def in_value_path(self, value):
        '''包含匹配value'''
        path_list = []
        self.find_in_value(self.target, value, path_list=path_list)
        return path_list

    def the_value_path(self, value):
        '''完全匹配value'''
        path_list = []
        self.find_the_value(self.target, value, path_list=path_list)
        return path_list

    def the_key_path(self, value):
        '''只查找key'''
        path_list = []
        self.find_the_key(self.target, value, path_list=path_list)
        return path_list
