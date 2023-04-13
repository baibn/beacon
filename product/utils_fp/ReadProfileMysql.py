# -*- coding: UTF-8 -*-
__author__ = 'huangyunpeng'

import pymysql
import sys
from sshtunnel import SSHTunnelForwarder
#from DealRawData import *
#from Encrypt import FpEncode7

def ReadProfileMysql(tzip,sshname,sshkey,originalKey,field):
    #print type(tzip),type(sshname),type(sshkey),type(originalKey),type(field)
    with SSHTunnelForwarder((str(tzip),22),
                                ssh_username = str(sshname),
                                ssh_pkey = str(sshkey),
                                remote_bind_address=('10.66.191.34',3306)
    ) as tunnel:
        conn = pymysql.connect(host='127.0.0.1',port=tunnel.local_bind_port,user='root',password='shumeitest2018',db='storage_profile_tel_cluster',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = "select * from storage_cluster where originalKey='profile:smid:%s' and field='%s';"%(str(originalKey).strip('\"').strip('\"'),str(field))
        print (sql)
        cursor.execute(sql)
        info = cursor.fetchone()
        print (info)
        print((type(info)))
        cursor.close()
        conn.close()
    if info == None:
        return 'notexist'
    else:
        return 'exist'

def DeleteProfile(tzip,sshname,sshkey):
    #print type(tzip),type(sshname),type(sshkey),type(originalKey),type(field)
    with SSHTunnelForwarder((str(tzip),22),
                                ssh_username = str(sshname),
                                ssh_pkey = str(sshkey),
                                remote_bind_address=('10.66.191.34',3306)
    ) as tunnel:
        conn = pymysql.connect(host='127.0.0.1',port=tunnel.local_bind_port,user='root',password='shumeitest2018',db='storage_profile_tel_cluster',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = "truncate storage_cluster;"
        print (sql)
        cursor.execute(sql)
        info = cursor.fetchone()
        print (info)
        cursor.close()
        conn.close()
    if info == None:
        print ('error')
    else:
        print ('ok')

def Syspath():
    return sys.path

def ReadFeatureLog(field,info):
    if field in info:
        return 'exist'
    else:
        return 'notexist'

if __name__ == '__main__':
    '''
    rootpath = GetPwd()
    toolpath = StrReplace(rootpath + '/library/fp-enc-tool.jar')
    datapath = StrReplace(rootpath + '/library/data.txt')
    keypath = StrReplace(rootpath + '/library/online_pub')
    resultpath = StrReplace(rootpath + '/data/resultdata.txt')
    configpath = StrReplace(rootpath + '/conf/config.json')
    rawdatapath = StrReplace(rootpath + '/data/rawdata.json')
    #body = FpEncode7(toolpath, org, keypath, datapath)
    result = ReadProfileMysql('tz-bj.fengkongcloud.cn','huangyunpeng','/Users/huangyunpeng/git/test-tianwang-fingerprint/ssh/ishumei-id_rsa','20181011145410e4070ba70b31c07bba9767d8d98d77db0121d157a8879fe5','test_multi_boxing')
    if result == None:
        print 'Profile is error!'
    else:
        print 'OK'
        '''
