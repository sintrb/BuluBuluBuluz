# -*- coding: UTF-8 -*
'''
Created on 2013-9-14

@author: RobinTang
'''

from sinlibs.tools.ynulib import search_books
from sinlibs.db.dbbase import get_connect
from sinlibs.db.SinDBAccess import SinDBAccess
from time import time

SPLITLINE = '-------------'
BOTTOMHELP = '你可以发送问号(?)给我'
BOTTOMHELPFULL = '%s\n%s'%(SPLITLINE, BOTTOMHELP)

tb_event = 'tb_bulu_event'
tpl_event = {
			'userid':'char(32)',
			'event':'char(32)',
			'time': int(time())
			}

tb_message = 'tb_bulu_message'
tpl_message = {
			'userid':'char(32)',
			'message':'',
			'time':int(time())
			}


def handlemessage(user, msg):
# 	dbcon = get_connect()
# 	dba = SinDBAccess(dbcon, debug=True)
# 	dba.create_table(tb_event, tpl_event, new=True)
# 	dba.create_table(tb_message, tpl_message, new=True)

	rets = '"%s"未找到\n%s'%(msg, BOTTOMHELPFULL)
	try:
		keyword = msg.strip()
		if len(keyword) > 0:
			if keyword=='?' or keyword == '？':
				return '目前支持云大图书搜索.\n告诉我书名或关键字即可.\n网页版<a href="http://bulubulubuluz.sinaapp.com/">BuluBuluBuluz</a>'
			if keyword=='who':
				return user
			books = search_books(keyword)
			ixs = []
			bmp = {}
			for book in books:
				if book['index'] and len(book['index']):
					ixs.append(book['index'])
					bmp[book['index']] = book
			if len(ixs):
				ixs.sort()
				spl = '\n%s\n'%SPLITLINE
				bks = spl.join(['%s (%s)'%(bmp[ix]['name'], bmp[ix]['index']) for ix in ixs])
				rets = '>>%s :%d条\n%s'%(keyword, len(ixs), bks)
	except:
		pass
	return rets

def whensubscribeevent(user, ctype='weixin'):
	'''
	用户订阅
	'''
	print '--------->subscribe: %s' % user
	return '欢迎订阅BuluBuluBuluz\n%s' % BOTTOMHELPFULL

def whenunsubscribeevent(user, ctype='weixin'):
	'''
	用户取消订阅
	'''
	print '--------->unsubscribe: %s' % user
	return ''


if __name__ == "__main__":
	handlemessage('user', 'msg')










