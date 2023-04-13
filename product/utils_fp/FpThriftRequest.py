# coding=utf-8
import sys
import json
import uuid
import time
import random

sys.path.append('fgen')
from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from .fgen.prediction import Predictor
from .fgen.prediction.ttypes import *


class RequestKeyWords(object):
    def __init__(self, host, port, data, type, serviceId, org, operation):
        self.host = host
        self.port = int(port)
        self.org = org
        self.serviceId = serviceId
        self.type = type
        self.data = data
        self.operation = operation

    def reqId(self):
        reuuid = uuid.uuid1()
        requestId = str(reuuid)
        return requestId.translate(None, '-')

    def reqdata(self):
        request = PredictRequest()  ##不需要改
        request.requestId = self.reqId()
        request.serviceId = self.serviceId
        request.type = self.type
        request.organization = self.org
        request.appId = 'default'
        request.eventId = 'default_eventId'
        request.tokenId = 'default_tokenId'
        request.timestamp = int(time.time())
        request.data = self.data
        request.operation = self.operation
        request.tags = 'default_tags'
        return request

    def client(self):
        transport = TSocket.TSocket(self.host, self.port)
        transport = TTransport.TFramedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = Predictor.Client(protocol)
        transport.open()
        try:
            request = self.reqdata()
            result = client.predict(request)  # 修改对应的API
            # print "requestdata",request
            # print "Result", result
            return result.detail.decode('utf-8')
            '''
            if result !=None:
                re_dict = {}
                # detail = result.detail.decode('utf-8')
                detail = result.detail
                re_dict["detail"] = json.loads(detail)
                re_dict["score"] = result.score
                re_dict["riskLevel"] = result.riskLevel
                re_dict["requestId"] = request.requestId
                return re_dict 
            '''
        except PredictException as ex:
            ex_dict = {}
            ex_dict["resquestId"] = request.requestId
            # ex_dict["code"] = ex.code
            ex_dict["message"] = ex.message
            # print "requestId = %s,code = %s,reslut = %s" %(reqId(),ex.code,ex.message)
            return ex_dict
        except TApplicationException as e:
            print()
            "requset err", e
        except:
            s = sys.exc_info()
            print()
            "err %s happened line is %d" % (s[1], s[2].tb_lineno)


def thrift_request(ip, port, data, type='default_type', serviceId='DEVICE_PROFILE', org='IkzxwQ4vofwwvFqC8ir2',
                   operation=None):
    '''
    Set thrift request:

    Example:
    |${result} |thrift request |127.0.0.1 |8003 |{"XXX":"XX"} |AD |POST_TEXT |IkzxwQ4vofwwvFqC8ir2| write |tags|
    |${result} |thrift request |127.0.0.1 |8003 |{} |
    '''
    try:
        re_dict = {}
        request = RequestKeyWords(ip, port, data, type, serviceId, org, operation)
        result = request.client()
        # str =  json.loads(json.dumps(result))
        return result

    except:

        s = sys.exc_info()
        return "error is %d line: %s" % (s[2].tb_lineno, s[1])


def GetJsonValueDiy(path):
    json_data = open(path).read()
    # data_dict = json.loads(json_data)
    return json_data


if __name__ == '__main__':
    try:
        filepath = "fpdata.json"
        ip = "10.141.48.108"
        port = "10240"
        type = "device"
        serviceId = "DEVICE_PROFILE"
        organization = "IkzxwQ4vofwwvFqC8ir2"
        data = str(GetJsonValueDiy(filepath))
        operation = "predict"
        result = thrift_request(ip, port, data, type, serviceId, organization, operation)
        print()
        result
    except IndexError as e:
        print()
        e
    except:
        s = sys.exc_info()
        print()
        " %s, happened line is %d" % (s[1], s[2].tb_lineno)
