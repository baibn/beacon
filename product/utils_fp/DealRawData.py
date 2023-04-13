# -*- coding: UTF-8 -*-

import json
import jsonpath
import os


#获取测试工程绝对路径
def GetPwd():
    pwd = os.getcwd()#获取启动路径
    print (pwd)
    if 'testcase' in pwd:
        pwd_fin = pwd.rstrip('testcase/')#通过启动路径获取上一级路径
        # return pwd_fin
    return pwd

#路径分隔符处理
def StrReplace(str):
    new_str = str.replace("\\","/")#将windows路径中的'\'符号替换成'/'
    return new_str

#从原始数据文件中读取数据
def GetJsonValueDiy(path):
    json_data = open(path).read()
    data_dict = json.loads(json_data)
    return data_dict

#使用配置文件中的数据更新原始数据
def ChangeJsonValue(configdata,rawdata,resultpath,datatype):
    x = 0
    for key in configdata:
        print (key)
        method = '$..' + str(key) + '.*'
        print (method)
        keydata = jsonpath.jsonpath(configdata,method)
        print (keydata)
        if keydata != False:
            for i in keydata:
                new_rawdata = []
                rawdata[key] = i
                new_rawdata.append(rawdata)
                if str(datatype) == 'android':
                    filename = str(resultpath) + 'data_' + str(x) + '.txt'
                elif str(datatype) == 'ios':
                    filename = str(resultpath) + 'data_ios_' + str(x) + '.txt'
                elif str(datatype) == 'web':
                    filename = str(resultpath) + 'data_web_' + str(x) + '.txt'
                else:
                    filename = str(resultpath) + 'data_weapp_' + str(x) + '.txt'
                x = x + 1
                #print filename
                f = open(filename,'w')
                new_rawdata = json.dumps(new_rawdata).strip('[').strip(']')
                f.writelines(new_rawdata)
                f.close()
        else:
            print ('keydata is empty char!')
    return x

def GetScreenConfig(configdata,rawdata,resultpath):
    rawdata = json.dumps(rawdata)
    filename = str(resultpath) + 'ios_screen_data.txt'
    f = open(filename, 'w+')
    for key in configdata:
        #print key
        method = '$..' + str(key) + '.*'
        #print method
        keydata = jsonpath.jsonpath(configdata, method)
        #print keydata
        for i in keydata:
            if len(i) == 7:
                if i[3] == '_' and i[4] != '_':
                    height = i[0] + i[1] + i[2]
                    width = i[4] + i[5] + i[6]
            elif len(i) == 8:
                if i[3] != '_' and i[4] == '_':
                    height = i[0] + i[1] + i[2] + i[3]
                    width = i[5] + i[6] + i[7]
                else:
                    height = i[0] + i[1] + i[2]
                    width = i[4] + i[5] + i[6] + i[7]
            else:
                height = i[0] + i[1] + i[2] + i[3]
                width = i[5] + i[6] + i[7] + i[8]
            print(("key is :" + key + " height is : "+ height + " width is :"+ width))
            new_rawdata = rawdata.replace('iPhone11,6',key)
            new_rawdata = new_rawdata.replace('896',height)
            new_rawdata = new_rawdata.replace('414', width)
            f.write(new_rawdata)
    f.close()

#反转数据
def DeGetScreenConfig(configdata,rawdata,resultpath):
    rawdata = json.dumps(rawdata)
    filename = str(resultpath) + 'de_ios_screen_data.txt'
    f = open(filename, 'w+')
    for key in configdata:
        #print key
        method = '$..' + str(key) + '.*'
        #print method
        keydata = jsonpath.jsonpath(configdata, method)
        #print keydata
        for i in keydata:
            if len(i) == 7:
                if i[3] == '_' and i[4] != '_':
                    width = i[0] + i[1] + i[2]
                    height = i[4] + i[5] + i[6]
            elif len(i) == 8:
                if i[3] != '_' and i[4] == '_':
                    width = i[0] + i[1] + i[2] + i[3]
                    height = i[5] + i[6] + i[7]
                else:
                    width = i[0] + i[1] + i[2]
                    height = i[4] + i[5] + i[6] + i[7]
            else:
                width = i[0] + i[1] + i[2] + i[3]
                height = i[5] + i[6] + i[7] + i[8]
            print(("key is :" + key + " height is : "+ height + " width is :"+ width))
            new_rawdata = rawdata.replace('iPhone11,6',key)
            new_rawdata = new_rawdata.replace('896',height)
            new_rawdata = new_rawdata.replace('xxx',width)
            f.write(new_rawdata)
    f.close()

if __name__ == '__main__':
    filename =  '/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/ios_screen/'
    rawdatapath = '/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/ios-encode0-rawdata.json'
    filepath = '/Users/huangyunpeng/git/test-tianwang-fingerprint-new/conf/ios_screen_config.json'
    configdata = GetJsonValueDiy(filepath)
    rawdata = GetJsonValueDiy(rawdatapath)
    #GetScreenConfig(configdata,rawdata,filename)
    DeGetScreenConfig(configdata, rawdata, filename)




