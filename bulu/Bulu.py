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
			'userid':'char(128)',
			'event':'char(32)',
			'eventid':0,
			'type':'char(32)',
			'typeid':0,
			'time': int(time())
			}

EVENT_SUBSCRIBE = 1
EVENT_UNSUBSCRIBE = 2

EVENT_TYPE_WEIXIN = 1
EVENT_TYPE_WEB = 2

EVENT_TYPEMAP = {
				'weixin':EVENT_TYPE_WEIXIN,
				'web':EVENT_TYPE_WEB
				}



tb_message = 'tb_bulu_message'
tpl_message = {
			'userid':'char(128)',
			
			'type':'char(32)',
			'typeid':0,
			
			'dir':0,
			'message':'',
			'time':int(time())
			}

MESSAGE_TYPE_TEXT = 1
MESSAGE_TYPE_ERROR = 2


MESSAGE_DIR_UP = 1
MESSAGE_DIR_DOWN = 2
MESSAGE_DIR_INTER = 3


def reset_all():
	dbcon = get_connect()
	dba = SinDBAccess(dbcon, debug=True)
	dba.create_table(tb_event, tpl_event, new=True)
	dba.create_table(tb_message, tpl_message, new=True)

def handlemessage(user, msg):
	if msg=='.reset' and user=='ofYB4jt9Sk0uIY8tv2nrluSH6jcc':
		# 该操作很危险，会重置数据库，只允许特定用户
		reset_all()
		return 'reset ok'
	dbcon = get_connect()
	dba = SinDBAccess(dbcon, debug=False)
	dba.add_object(tb_message, {
  							'userid':user, 
  							'message':msg, 
  							'type':'text', 
  							'typeid': MESSAGE_TYPE_TEXT, 
  							'dir':MESSAGE_DIR_UP,
  							'time':int(time())
  							}
  				)
	
	rets = '"%s"未找到\n%s'%(msg, BOTTOMHELPFULL)
	try:
		keyword = msg.strip()
		if len(keyword) > 0:
			if keyword=='?' or keyword == '？':
				rets = '目前支持云大图书搜索.\n告诉我书名或关键字即可.\n网页版<a href="http://bulubulubuluz.sinaapp.com/">BuluBuluBuluz</a>'
			elif keyword=='who':
				rets = user
			else:
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
		rets = 'Oops...\n内部出错\n请重新试  ~_~\n%s'%BOTTOMHELPFULL
		dba.add_object(tb_message, {
	  							'userid':user, 
	  							'message':msg, 
	  							'type':'error', 
	  							'typeid': MESSAGE_TYPE_ERROR, 
	  							'dir':MESSAGE_DIR_INTER,
	  							'time':int(time())
	  							}
	  				)
	dba.add_object(tb_message, {
  							'userid':user, 
  							'message':rets, 
  							'type':'text', 
  							'typeid': MESSAGE_TYPE_TEXT, 
  							'dir':MESSAGE_DIR_DOWN,
  							'time':int(time())
  							}
  				)
	
	return rets

def whensubscribeevent(user, ctype='weixin'):
	'''
	用户订阅
	'''
	dbcon = get_connect()
	dba = SinDBAccess(dbcon, debug=False)
	typeid = 0
	try:
		typeid = EVENT_TYPEMAP[ctype]
	except:
		pass

	dba.add_object(tb_event, {
							'userid': user,
							'event':'subscribe',
							'eventid':EVENT_SUBSCRIBE,
							'type': ctype,
							'typeid': typeid,
							'time': int(time())
							})
	return '欢迎订阅BuluBuluBuluz\n%s' % BOTTOMHELPFULL

def whenunsubscribeevent(user, ctype='weixin'):
	'''
	用户取消订阅
	'''
	dbcon = get_connect()
	dba = SinDBAccess(dbcon, debug=False)
	typeid = 0
	try:
		typeid = EVENT_TYPEMAP[ctype]
	except:
		pass

	dba.add_object(tb_event, {
							'userid': user,
							'event':'unsubscribe',
							'eventid':EVENT_UNSUBSCRIBE,
							'type': ctype,
							'typeid': typeid,
							'time': int(time())
							})
	return ''


if __name__ == "__main__":
	whensubscribeevent('user', 'msg')










