# -*- coding: UTF-8 -*
'''
Created on 2013-9-29

@author: RobinTang
'''

import MySQLdb

def get_connect(dbn='dbp'):
    '''获取数据库连接'''
    try:
    #    尝试对SAE的数据库进行连接
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root123', db='buluz', port=3306)
    except:
    #    连接失败，那么就认为是在本地环境
        conn = MySQLdb.connect(host='172.16.0.200', user='trb', passwd='123456', db='buluz', port=3306)
    conn.set_character_set('utf8')
    return conn
