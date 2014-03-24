# -*- coding: UTF-8 -*
'''
Created on 2014-3-24

@author: RobinTang
'''
import datetime
import time

def str2dtime(s, tpl='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(s, tpl)
def dtime2str(dt, tpl='%Y-%m-%d %H:%M:%S'):
    return time.strftime(tpl, dt.timetuple())
def stamp2str(stamp, tpl='%Y-%m-%d %H:%M:%S'):
    return time.strftime(tpl, time.localtime(stamp))
def dtime2stamp(dt):
    return time.mktime(dt.timetuple())


if __name__ == '__main__':
    now = datetime.datetime.now()
    snow = dtime2str(now)
    tnow = dtime2stamp(now)
    assert tnow == dtime2stamp(str2dtime(snow))
    print stamp2str(tnow)
    print dtime2str(now)
    