# -*- coding: UTF-8 -*
'''
Created on 2013-9-14

@author: RobinTang
'''

from sinlibs.tools.ynulib import search_books

SPLITLINE = '-------------'
BOTTOMHELP = '你可以发送问号(?)给我'
BOTTOMHELPFULL = '%s\n%s'%(SPLITLINE, BOTTOMHELP)

def handlemessage(user, msg):
    rets = '"%s"未找到\n%s'%(msg, BOTTOMHELPFULL)
    try:
        keyword = msg.strip()
        if len(keyword) > 0:
            if keyword=='?' or keyword == '？':
                return '网页版\nhttp://bulubulubuluz.sinaapp.com/'
            if keyword=='who':
                return user
            books = search_books(keyword)
            ixs = []
            bmp = {}
            for book in books:
                if book['index'] and len(book['index']):
                    ixs.append(book['index'])
                    bmp[book['index']] = book
            ixs.sort()
            spl = '\n%s\n'%SPLITLINE
            bks = spl.join(['%s (%s)'%(bmp[ix]['name'], bmp[ix]['index']) for ix in ixs])
            rets = '>>%s :\n%s'%(keyword, bks)
    except:
        pass
    return rets













