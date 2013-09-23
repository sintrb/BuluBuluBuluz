# -*- coding: UTF-8 -*
'''
Created on 2013-6-22

@author: RobinTang
'''
import random

def strbetweenrange(s, fre, suf, starti=0, contain=False):
    si = s.find(fre, starti) + len(fre)
    if si<len(fre):
        return None
    ei = s.find(suf, si)
    if ei<0:
        return None
    if contain:
        si = si - len(fre)
        ei = ei + len(suf)
    return (si,ei)
def strbetween(s, fre, suf, starti=0, contain=False):
    rg = strbetweenrange(s, fre, suf, starti, contain)
    if rg:
        return s[rg[0]:rg[1]]
    else:
        return None

def gentoken(l=10):
    ss = 'abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()~'
    tk = ''.join([random.choice(ss) for i in range(0, l)])
    return tk


if __name__ == '__main__':
    print strbetween('12startereeand', 'start', 'end')
    print gentoken()
