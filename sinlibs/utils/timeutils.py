# -*- coding: UTF-8 -*
'''
Created on 2014-3-24

@author: RobinTang
'''
import datetime
import time

def str2dtime(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
def dtime2str(dt):
    return time.strftime('%Y-%m-%d %H:%M:%S', dt.timetuple())
def stamp2str(stamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stamp))
def dtime2stamp(dt):
    return time.mktime(dt.timetuple())


if __name__ == '__main__':
    now = datetime.datetime.now()
    snow = dtime2str(now)
    tnow = dtime2stamp(now)
    assert tnow == dtime2stamp(str2dtime(snow))
    print stamp2str(tnow)
    print dtime2str(now)
    