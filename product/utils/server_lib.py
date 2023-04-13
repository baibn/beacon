import paramiko
import time
import re

ssh_conf = {
    "Host": "118.89.221.77",
    "Port": 22,
    "User": "work",
    "Pwd": "shumeitest2019"
}


class ServerLibrary(object):
    def __init__(self, ssh_conf):
        self.host = ssh_conf['Host']
        self.port = ssh_conf['Port']
        self.username = ssh_conf['User']
        self.passwd = ssh_conf['Pwd']

    def server_connect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.passwd, timeout=10)
        self.__ssh = ssh
        self.channel = self.__ssh.invoke_shell()
        self.channel.settimeout(10)

    def server_query(self, filepath, requestid, obj_str, regex, delay=1):
        """
        filepath: /mnt/work/engine/re-video/dist/log/data-re-video.log

        requestid: requestid

        obj_str: 过滤条件（多个用","分割）

        regex: (?<=data=)(.*)(?=\r)

        delay: 1
        """
        command = 'cat ' + filepath + ' | grep ' + requestid
        obj_list = [grep_str for grep_str in obj_str.split(',')]
        for grep_str in obj_list:
            command = command + ' | grep ' + grep_str
        command = command + '\r'
        print("日志查询命令：{}".format(command))
        self.channel.send(command)
        time.sleep(delay)
        result = self.channel.recv(999999).decode('utf-8')
        pattern = re.compile(regex)
        print(pattern.findall(result))
        return pattern.findall(result)

    def server_close(self):
        self.__ssh.close()


if __name__ == '__main__':
    ssh = ServerLibrary(ssh_conf)
    filepath = "/mnt/work/engine/re-video/dist/log/data-re-video.log"
    requestid = "b75672af5d8dcee3db573df3ab9e0485"
    reg = "(?<=data=)(.*)(?=\r)"
    obj = "INFO"
    ssh.server_connect()
    print(ssh.server_query(filepath, requestid, obj, reg))
