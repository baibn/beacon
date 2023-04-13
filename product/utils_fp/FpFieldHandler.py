# -*- coding: UTF-8 -*-

import os
import json

class FpFieldHandler(object):
    def profile_read(sefl,key_path,profile_ip,profile_port,org,deviceId):
        command = '%s -target_profile_host=%s -target_profile_port=%s -organization=%s -event_id=device  -service_id=DEVICE_PROFILE -data=\'{"__request_type__":"GET_PROFILE","table":"profile:smid","key":%s,"data_type":"KMAP"}\'' % (key_path,profile_ip,profile_port,org,deviceId)
        f = os.popen(command)
        re = f.read().rstrip()
        print (command)
        print (re)
        return re

    def profile_delete(self,key_path,profile_ip,profile_port,deviceId):
        command = '%s -target_profile_host=%s -target_profile_port=%s -operations=DELETE_PROFILE  -data=\'{"DELETE_PROFILE":[{"table":"profile:smid","key":%s}]}\'' % (
        key_path, profile_ip, profile_port,deviceId)
        f = os.popen(command)
        re = f.read().rstrip()
        print (re)

    def field_check(self,profile_result,field):
        print (field)
        print((type(field)))
        profile_result = json.loads(profile_result)
        if field in profile_result["result"]:
            return "True"
        else:
            return "False"

if __name__ == "__main__":
    fp = FpFieldHandler()
    fp.profile_read("test","123.206.31.98","7000","RlokQwRlVjUrTUlkIqOg","2019042815245351fc5f7c6a9e988d54fdd0acf56ee5d001796f0ae29d64e7")
    fp.profile_delete("test","123.206.31.98","7000","2019042815245351fc5f7c6a9e988d54fdd0acf56ee5d001796f0ae29d64e7")