# -*- coding: UTF-8 -*-

import json
import ast


class FpDataDealer(object):
    def data_update(self, inputdata, key, value):
        inputdata = json.loads(inputdata)
        inputdata[key] = value
        print("+++++++++++")
        return inputdata

    def data_update_progressive(self, inputdata, key, value):
        print(key)
        key = str(key).split("-")
        root = key[0]
        key = key[1]
        inputdata = json.loads(inputdata)
        inputdata[root][key] = value
        print("+++++++++++")
        return inputdata

    def data_add(self, inputdata):
        inputdata = json.loads(inputdata)
        print("+++++++++++")
        return "test"

    def data_delete(self, inputdata, key):
        print(key)
        key = str(key)
        inputdata = json.loads(inputdata)
        inputdata.pop(key)
        print("+++++++++++")
        return inputdata

    def data_delete_progressive(self, inputdata, key):
        print(key)
        key = str(key).split("-")
        root = key[0]
        key = key[1]
        print(root)
        print(key)
        inputdata = json.loads(inputdata)
        inputdata[root].pop(key)
        print("+++++++++++")
        return inputdata


if __name__ == "__main__":
    test_dict = '{"data":{"fpEncode":7},"test":"1"}'
    test_str = 'organization=RlokQwRlVjUrTUlkIqOg&smdata=WC39ZUyXRgdG0spD3GJ5TXXy%2Ffst7ePVcr4kvIENMMeuBayvwtDX99QYCYTaRjrvC3zZayjW5XBjHsXwvHRbMJig99adrKMIaFyT39NTZ%2FuIhKF8yjWIWTKGxdUOPvm46aPLn3vXc1%2FbqaAGEOzRiNygG8SGwpjgpX0BRyF6yvBDdfsHxvYNkDyq%2FmSI9FDQTjTzx5WQlfv1MwuaIi%2FXvruki7DYDsmg3nvcRVMo1CbER8VG18sAReVFdiCYpoD4C6%2BjYvruhwydFeDzbU7fW%2BFXCBTkwxWQBtqzcSg4s3jseF5SjS8nHVp88zh9n8kYv%2FSkqwzdnRv3QXE9%2Fr3Z1en2DAyDhEJ30%2BwIumPJcLc%2FR5fWpGdnSNNZMKgNLtntzBLlTeHY5oVkP%2F0%2F1JNxyOIOSAfWuWOD056Uq4shcrpXeZtM0zqfaheSa6NZINWiHuGqKihAhBfk7mumNbHIv8NeL%2FSB5vayE03ugSwnVXSCqVSRPjJTsvpnZMN6id4ikdvlaBoyK%2B7cmlL2u2NMdfvMnE%2BS%2B8JxB49A4UQcJReo%2Bcy3szd1Hw25fad72xSnu6PoKMBpzdvP5tWUaKSbmHBXm%2FE%2By4XAD0m6pJ0rU3aR395oReIy3W2ddHL6RXUQDnuKOyDG4joFHA%2BxMA%2BP6KQpx9DLjX%2FjVt1j19RP0Z%2BA9XYK%2Bju6XDSS99lHhq%2BhlhYQBcwXb4QxwyUcvlhAKWTu3VbttirTuE5elhy1sMvgAX%2Bta1xoiUXVy%2BKicUgdzB2zfyTriO3th9HJJLmkyb8bugg1u85cQlu3O12ZgErYw22tohz1X0MYuAOwgUvBOlfU2EYmdJk6rLdYNqj7Mj%2BXLyaEb3NcDS7l2JpiA0z0i5MvQFgtx5cvtNser%2FqgUP%2BA77QdiHj3kJBqm4%2BhQtxW0BLaDm8iiFyd6Ym6RrudX6Px4tZ5mS136VZlLcITqeUah2WTrOzEfkXDAcefDsxb3OfOMB7gJH%2B1dkme4UBQ1GbdI0bPJsNnii3nApun1o5u2gC2zJbWT6NM5oVzhcejo9BpBY8ENQIyk658p9x6ewNNoHs3XAioLrtALLZfY5Jro1kg1aIdKuFKieYJYUFoBzxT3CUlbZfAFsyL6nej18v4lWNFTCPW2YhWGKkMHtPkJy10PYWK6S8vyMMfyPTeEFQAQp%2Fl7dNHULBaA6%2BLwFUf4hyiEPFd99bgupoDcnOvfCKvEUKB5%2B4GtonyEStRJlyDvkfPL%2Bs47fhIUa1GBKLvCxpxq1mOHWTyhTuf1Kd5eipw2pMymuaadEfFxSUkB9IEvEG3fOmsNSLB8cXpVxHEUxXQeZ8U%2Fv2r5Ge61PiUQ%2BQSpF%2FA%3D1487577677129&os=web&version=2.0.0'
    fp = FpDataDealer()
    # re = fp.data_delete_progressive(test_dict,"data-fpEncode")
    re = fp.data_split_delete(test_str, 1)
    print(re)
