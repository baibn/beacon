# -*- coding: UTF-8 -*-

import json
import jsonpath
import os
from .DealRawData import GetJsonValueDiy

android_mapping_all = {
"rtype":"a1",
"smid":"a2",
"privacy":"a3",
"smseq":"a4",
"apputm":"a5",
"os":"a6",
"sdkver":"a7",
"sdk_flavor":"a8",
"t":"a9",
"osver":"a10",
"appId":"a11",
"pid":"a12",
"model":"a13",
"abtmac":"a14",
"axposed":"a15",
"ainfo":"a16",
"net":"a17",
"props":"a18",
"bssid":"a19",
"imei":"a20",
"tn":"a21",
"imei1":"a22",
"imei2":"a23",
"adid":"a24",
"imsi":"a25",
"mac":"a26",
"apps":"a27",
"whiteapp":"a28",
"band":"a29",
"ssid":"a30",
"wifiip":"a31",
"cpuCount":"a32",
"cpuModel":"a33",
"cpuFreq":"a34",
"cpuVendor":"a35",
"screen":"a36",
"brightness":"a37",
"appver":"a38",
"appname":"a39",
"boot":"a40",
"name":"a41",
"proc":"a42",
"brand":"a43",
"network":"a44",
"operator":"a45",
"sys":"a46",
"sensor":"a47",
"mem":"a48",
"iccid":"a49",
"cell":"a50",
"aps":"a51",
"riskapp":"a52",
"riskdir":"a53",
"emu":"a54",
"ccmd5":"a55",
"signdn":"a56",
"signhash":"a57",
"virtual":"a58",
"virtualcnt":"a59",
"virtualuid":"a60",
"virtualproc":"a61",
"files":"a62",
"input":"a63",
"acc":"a64",
"cost":"a65",
"ip_cache":"a67",
"fc_t":"a68",
"availableSpace":"a69",
"freeSpace":"a70",
"totalSpace":"a71",
"battery":"a72",
"mockLoc":"a73",
"debugger":"a74",
"debuggable":"a75",
"proxyV2":"a76",
"xp_callback":"a77",
"xp_cache":"a78",
"err":"a79",
"sid":"a80",
"aenc":"a81",
"ainfoMd5":"a82",
"permission":"a83"
}

android_ainfo_mapping = {
"gothk":"b1",
"resett":"b2",
"ds_md5":"b3",
"ds_md52":"b4",
"vf_md5":"b5",
"sb_md5":"b6",
"vl_md5":"b7",
"sf_md5":"b8",
"font_md5":"b9",
"font_md52":"b10",
"ap_mac":"b11",
"wifi_mac":"b12",
"sys_props":"b13",
"root":"b15",
"tmpr_fw":"b16",
"abi":"b17",
"riskfile":"b18",
"hook":"b19",
"is_art":"b20",
"hook_java":"b21",
"bootId":"b22",
"randomKey":"b23",
"is_vpn":"b24"
}

mapping_all = {
    "smid":"a1",
    "smseq":"a2",
    "rtype":"a3",
    "os":"a4",
    "sdkver":"a5",
    "t":"a6",
    "osver":"a7",
    "model":"a8",
    "idfv":"a9",
    "idfa":"a10",
    "track":"a11",
    "boot" :"a12",
    "root" :"a13",
    "is_vpn" :"a14",
    "appname" :"a15",
    "appver" :"a16",
    "appversion" :"a17",
    "acCode":"a18",
    "stCode" :"a19",
    "rmCode" :"a20",
    "name" :"a21",
    "totalSpace" :"a22",
    "freeSpace" :"a23",
    "memory" :"a24",
    "brightness" :"a25",
    "battery" :"a26",
    "width" :"a27",
    "height" :"a28",
    "scaledDensity" :"a29",
    "networkType" :"a30",
    "ssid" :"a31",
    "bssid" :"a32",
    "dns" :"a33",
    "countryIso" :"a34",
    "mcc" :"a35",
    "mnc" :"a36",
    "languages" :"a37",
    "gps" :"a38",
    "orientation" :"a39",
    "accessory" :"a40",
    "md5" :"a41",
    "tn" :"a42",
    "riskapp" :"a43",
    "riskdir" :"a44",
    "s_c" :"a45",
    "sid" : "a48",
    "apputm" :"a46",
    "appId" :"a47",
    "mobileCountryCode":"s1",
    "mobileNetworkCode":"s2",
    "isoCountryCode":"s3",
    "reachabilityForInternetConnection":"s4",
    "valueWithError":"s5",
    "isReachableViaWiFi":"s6",
    "localizedModel":"s7",
    "systemVersion":"s8",
    "platform":"s9",
    "carrierName":"s10",
    "hwmodel":"s11",
    "currentRadioAccessTechnology":"s12",
    "name":"s13",
    "model":"s14",
    "value":"s15",
    "isReachableViaWWANP":"s16",
    "identifierForVendor":"s17",
    "loc":"s18",
    "locDele":"s19",
    "fname":"k1",
    "fbase":"k2",
    "opcode":"k3",
    "saddr":"k4",
    "sname":"k5"
}

ios_mapping = {
    "smid":"a1",
    "smseq":"a2",
    "rtype":"a3",
    "os":"a4",
    "sdkver":"a5",
    "t":"a6",
    "osver":"a7",
    "model":"a8",
    "idfv":"a9",
    "idfa":"a10",
    "track":"a11",
    "boot" :"a12",
    "root" :"a13",
    "is_vpn" :"a14",
    "appname" :"a15",
    "appver" :"a16",
    "appversion" :"a17",
    "acCode":"a18",
    "stCode" :"a19",
    "rmCode" :"a20",
    "name" :"a21",
    "totalSpace" :"a22",
    "freeSpace" :"a23",
    "memory" :"a24",
    "brightness" :"a25",
    "battery" :"a26",
    "width" :"a27",
    "height" :"a28",
    "scaledDensity" :"a29",
    "networkType" :"a30",
    "ssid" :"a31",
    "bssid" :"a32",
    "dns" :"a33",
    "countryIso" :"a34",
    "mcc" :"a35",
    "mnc" :"a36",
    "languages" :"a37",
    "gps" :"a38",
    "orientation" :"a39",
    "accessory" :"a40",
    "md5" :"a41",
    "tn" :"a42",
    "riskapp" :"a43",
    "riskdir" :"a44",
    "s_c" :"a45",
    "sid" : "a48",
    "apputm" :"a46",
    "appId" :"a47"
}

f_mapping = {
    "mobileCountryCode":"s1",
    "mobileNetworkCode":"s2",
    "isoCountryCode":"s3",
    "reachabilityForInternetConnection":"s4",
    "valueWithError":"s5",
    "isReachableViaWiFi":"s6",
    "localizedModel":"s7",
    "systemVersion":"s8",
    "platform":"s9",
    "carrierName":"s10",
    "hwmodel":"s11",
    "currentRadioAccessTechnology":"s12",
    "name":"s13",
    "model":"s14",
    "value":"s15",
    "isReachableViaWWANP":"s16",
    "identifierForVendor":"s17",
    "loc":"s18",
    "locDele":"s19",
    "fname":"k1",
    "fbase":"k2",
    "opcode":"k3",
    "saddr":"k4",
    "sname":"k5"
}

###################################################################
#
#函数名：CheckMapResult
#参数：
#   before：解密前的数据
#   after：解密后的数据
#   mapping：映射表
#功能：判断解密前后的数据字段名是否在映射表中
#正确预期：解密前在映射表中的数据为空，解密前不在映射表中的数据应该为所有；
#         解密后在映射表中的数据为所有，解密后不在映射表中的数据为空
#
###################################################################

def CheckMapResult(before,after,mapping):
    before_in_mapping = []
    before_not_in_mapping = []
    after_in_mapping = []
    after_not_in_mapping = []
    for before_key in before:
        if before_key in mapping:
            before_in_mapping.append(before_key)
        else:
            before_not_in_mapping.append(before_key)
    if len(before_in_mapping) != 0:
        str = "ERROR"
    else:
        str = "OK"
    print (str)
    print(("解密前在映射表中的数据有: ",before_in_mapping,"\n"))
    print(("解密前不在映射表中的数据有: ",before_not_in_mapping,"\n"))
    for after_key in after:
        if after_key in mapping:
            after_in_mapping.append(after_key)
        else:
            after_not_in_mapping.append(after_key)
    if len(after_not_in_mapping) != 0:
        str2 = "ERROR"
    else:
        str2 = "OK"
    print (str2)
    print(("解密后在映射表中的数据有: ", after_in_mapping,"\n"))
    print(("解密后不在映射表中的数据有: ", after_not_in_mapping,"\n"))



def CheckMapContent(before,after,mapping,mapping2):
    success_mapping = []
    fail_mapping = []
    for after_key in after:
        if after_key == "cd":
            print((after_key,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"))
            continue
        if type(after[after_key]) == type(mapping):
           after_value = after[after_key]
           before_value = before[mapping[after_key]]
           for after_key_2 in after_value:
               if type(after_value[after_key_2]) == type(mapping):
                   print((after_value[after_key_2]))
                   print (after_key_2)
                   if (after_key_2 in mapping2) or (after_key_2 in mapping):
                       after_value_2 = after_value[after_key_2]
                       before_value_2 = before_value[mapping2[after_key_2]]
                       print (after_value_2)
                       print (before_value_2)
                       for after_key_3 in after_value_2:
                           if (after_key_3 in mapping2) or (after_key_3 in mapping):
                               if after_value_2[after_key_3] == before_value_2[mapping2[after_key_3]]:
                                   print(("3before = after",after_key_3))
                                   success_mapping.append(after_key_3)
                               else:
                                   print(("3before != after",after_key_3))
                                   fail_mapping.append(after_key_3)
                           else:
                               fail_mapping.append(after_key_3)
                   else:
                       fail_mapping.append(after_key_2)
               else:
                   if (after_key_2 in mapping2) or (after_key_2 in mapping):
                       if after_value[after_key_2] == before_value[mapping[after_key_2]]:
                           print ("2before = after")
                           success_mapping.append(after_key_2)
                       else:
                           print ("2before = after")
                   else:
                       fail_mapping.append(after_key_2)
        else:
            print((mapping[after_key]))
            print((type(after[after_key]),after[after_key]))
            if after[after_key] == before[mapping[after_key]]:
                print(("1before = after",after_key))
                success_mapping.append(after_key)
            else:
                print(("1before = after",after_key))
                fail_mapping.append(after_key)
    print(("映射成功的有： ",success_mapping))
    print(("映射失败的有： ",fail_mapping))



if __name__ == "__main__":
    before_data_path ="/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/MapToolData/before.json"
    after_data_path = "/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/MapToolData/after_all.json"
    #before_data_path = "/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/MapToolData/android_before_all.json"
    #after_data_path = "/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/MapToolData/android_after_all.json"
    #before_data_path = "/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/MapToolData/android_before_ainfo.json"
    #after_data_path = "/Users/huangyunpeng/git/test-tianwang-fingerprint-new/data/MapToolData/android_after_ainfo.json"

    before_data = GetJsonValueDiy(before_data_path)
    after_data = GetJsonValueDiy(after_data_path)
    #ios校验
    CheckMapResult(before_data,after_data,mapping_all)
    #CheckMapContent(before_data,after_data,ios_mapping,f_mapping)

    #android校验
    #CheckMapResult(before_data,after_data,android_mapping_all)
    #CheckMapContent(before_data,after_data,android_mapping_all,android_ainfo_mapping)

    # android_ainfo校验
    #CheckMapResult(before_data,after_data,android_ainfo_mapping)
    #CheckMapContent(before_data,after_data,android_ainfo_mapping,android_ainfo_mapping)


