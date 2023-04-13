# -*- coding: UTF-8 -*-

import os
import json


# import common.config as config

class FpEncoder(object):
    def __init__(self, toolpath, org, ainfokey, keypath, tempath):
        self.toolpath = toolpath
        self.org = org
        self.ainfokey = ainfokey
        self.keypath = keypath
        self.tempath = tempath

    def fpencode_4(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=4 -o=%s -s=%s' % (self.toolpath, self.org, self.tempath)
        print(command)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    def fpencode_7(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=7 -o=%s -a=%s -k=%s -s=%s' % (
            self.toolpath, self.org, self.ainfokey, self.keypath, self.tempath)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    def fpencode_9(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=9 -o=%s -a=%s -k=%s -s=%s' % (
            self.toolpath, self.org, self.ainfokey, self.keypath, self.tempath)
        print(command)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    def fpencode_10(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=10 -o=%s -k=%s -s=%s' % (
            self.toolpath, self.org, self.keypath + "ios_pub/", self.tempath)
        print(command)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    def fpencode_11(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=11 -o=%s -a=%s -k=%s -s=%s' % (
            self.toolpath, self.org, self.ainfokey, self.keypath, self.tempath)
        print(command)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    def fpencode_web(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=web -o=%s -s=%s' % (self.toolpath, self.org, self.tempath)
        print(command)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    def fpencode_weapp(self, rawdata):
        with open(self.tempath, 'w') as f:
            f.writelines(rawdata)
            f.close()
        command = 'java -jar %s -e -f=weapp -o=%s -s=%s' % (self.toolpath, self.org, self.tempath)
        print(command)
        f = os.popen(command)
        re = f.read().rstrip()
        # f.close()
        return re

    '''
    def FpEncode7_savedata(self,toolpath,org,ainfokey,keypath,datapath,resultpath):
        command = 'java -jar %s -e -f=7 -o=%s -a=%s -k=%s -s=%s > %s'%(toolpath,org,ainfokey,keypath,datapath,resultpath)
        #print "command is %s"%(command)
        re = os.system(command)
    

    def FpEncode7(self,toolpath,org,ainfokey,keypath,datapath):
        command = 'java -jar %s -e -f=7 -o=%s -a=%s -k=%s -s=%s'%(toolpath,org,ainfokey,keypath,datapath)
        #print("Command is : %s"%(command))
        #re = os.popen(command).read().rstrip()
        f = os.popen(command)
        re = f.read().rstrip()
        f.close()
        #print("Result is :%s"%(re))
        return re
   
    def FpEncode8_savedata(self,toolpath,org,keypath,datapath,resultpath):
        command = 'java -jar %s -e -f=8 -o=%s -k=%s -s=%s > %s'%(toolpath,org,keypath,datapath,resultpath)
        #print command
        re = os.system(command)
    

    def FpEncode8(self,toolpath,org,keypath,datapath):
        command = 'java -jar %s -e -f=8 -o=%s -k=%s -s=%s'%(toolpath,org,keypath,datapath)
        #print "Command is : %s"%(command)
        re = os.popen(command).read()
        #print "Result is :%s"%(re)
        return re

    def Fpencode4(self,toolpath,org,datapath):
        command = 'java -jar %s -e -f=4 -o=%s -s=%s'%(toolpath,org,datapath)
        #print "Command is : %s" % (command)
        re = os.popen(command).read()
        #print "Result is :%s" % (re)
        return re
    '''


if __name__ == "__main__":
    '''
    toolpath = config.tool_path
    org = config.organization_dict['test']
    ainfokey = config.ainfokey_dict['test']
    keypath = config.key_path
    datapath = config.data_path + "/temp.txt"

    fp = FpEncoder(config.rawdata,toolpath,org,ainfokey,keypath,datapath)
    print(fp.fpencode_7())
    '''
