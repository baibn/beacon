import pymysql
from sshtunnel import SSHTunnelForwarder
from product.config import Config
import json
import xml.etree.ElementTree


class ReadLibrary(object):
    @staticmethod
    def read_config(filepath):
        with open(filepath) as json_file:
            config_json = json.load(json_file)
        return config_json

    @staticmethod
    def get_xml_sql(sql_id, filepath):
        tree = xml.etree.ElementTree.ElementTree(file=filepath)
        for elem in tree.iterfind("command[@id='{0}']".format(sql_id)):
            sql = elem.text
            return sql

    @staticmethod
    def to_dict(json_str):
        return json.loads(json_str)


class DbLibrary(object):
    def __init__(self, database):
        conf = ReadLibrary.read_config(Config.sql_conf_path)
        # self.ssh_host = conf['MysqlSshC']['Host']
        # self.ssh_port = conf['MysqlSshC']['Port']
        # self.ssh_username = conf['MysqlSshC']['User']
        # self.ssh_pkey = Config.p_key_path

        self.mysql_host = conf['MysqlC']['Host']
        self.mysql_port = conf['MysqlC']['Port']
        self.mysql_user = conf['MysqlC']['User']
        self.mysql_password = conf['MysqlC']['Password']
        # self.server = SSHTunnelForwarder(ssh_address_or_host=(self.ssh_host, self.ssh_port),
        #                                  ssh_username=self.ssh_username,
        #                                  ssh_pkey=self.ssh_pkey,
        #                                  remote_bind_address=(self.mysql_host, self.mysql_port))
        # self.server.start()
        # for base in database.split(','):
        # self.db = pymysql.connect(host='127.0.0.1',
        #                           port=self.server.local_bind_port,
        #                           user=self.mysql_user,
        #                           password=self.mysql_password,
        #                           database=database)
        self.db = pymysql.connect(host=self.mysql_host,
                                  port=self.mysql_port,
                                  user=self.mysql_user,
                                  password=self.mysql_password,
                                  database=database)

    def db_select(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            if len(data) == 1:
                data = list(data[0].values())[0]
            else:
                data_list = []
                for key_value in data:
                    data_list.append(list(key_value.values())[0])
                data = data_list
            print(data)
        except Exception as err:
            data = tuple()
            print('select data error: ', err)
        finally:
            cursor.close()
        return data

    def db_insert(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            res = cursor.execute(sql)
            print(res)
            self.db.commit()
        except Exception as err:
            print('insert data error: ', err)
            self.db.rollback()
        finally:
            cursor.close()

    def db_delete(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            res = cursor.execute(sql)
            print(res)
            self.db.commit()
        except Exception as err:
            print('delete data error: ', err)
            self.db.rollback()
        finally:
            cursor.close()

    def db_update(self, sql):
        cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            res = cursor.execute(sql)
            print(res)
            self.db.commit()
        except Exception as err:
            print('update data error: ', err)
            self.db.rollback()
        finally:
            cursor.close()

    def db_close(self):
        self.db.close()


if __name__ == '__main__':
    db = DbLibrary('sentry')
    print(db.db_select("show tables;"))
