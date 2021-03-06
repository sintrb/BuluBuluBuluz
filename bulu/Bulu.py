# -*- coding: UTF-8 -*
'''
Created on 2013-9-14

@author: RobinTang
'''

from time import time
from SinLikeTerminal import SinLikeTerminal
from BuluFuncs import BOTTOMHELPFULL
import BuluFuncs
import traceback
from bulu.Adapters import BaseAdapter
config = {'debug':True}

slt = SinLikeTerminal()
slt.add_route('1', BuluFuncs.ynu_lib_search)
slt.add_route('1.echo', BuluFuncs.tool_echo)
slt.add_route('1.debug', BuluFuncs.tool_debug)
slt.add_route('1.config', BuluFuncs.tool_config)
slt.add_route('1.dev', BuluFuncs.tool_dev)


slt.refresh_allroute()
bulu_route = slt.route
del slt


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
MESSAGE_TYPE_UNKNOWN = 0
MESSAGE_TYPE_TEXT = 1
MESSAGE_TYPE_ERROR = 2
MESSAGE_TYPE_IMAGE = 3

MESSAGE_DIR_UP = 1
MESSAGE_DIR_DOWN = 2
MESSAGE_DIR_INTER = 3


def reset_all(ctx):
	dba = ctx.dba
	dba.create_table(tb_event, tpl_event, new=True)
	dba.create_table(tb_message, tpl_message, new=True)

def handlemessage(user, msg, ctx=None):
# 	if msg == '.reset':# and user == 'ofYB4jt9Sk0uIY8tv2nrluSH6jcc':
# 		# 该操作很危险，会重置数据库，只允许特定用户
# 		reset_all(ctx)
# 		return 'reset ok'
	dba = ctx.dba
	sttm = entm = 0
	dba.add_object(tb_message, {
  							'userid':user,
  							'message':msg,
  							'type':'text',
  							'typeid': MESSAGE_TYPE_TEXT,
  							'dir':MESSAGE_DIR_UP,
  							'time':int(time())
  							}
  				)
	rets = '未处理'
	try:
		kvdb = ctx.kvdb
		curslt = SinLikeTerminal(kvdb, bulu_route, debug=False)
		msg = msg.replace('？', '?')
		sttm = time()
		rets = curslt.process_message(user, msg, ctx)
# 		print 'll:%d'%len(rets)
		entm = time()
	except:
		errinfo = traceback.format_exc()
		print errinfo
		if 'debug' in config and config['debug']:
			rets = errinfo
		else:
			rets = 'Oops...\n内部出错\n请重新试  ~_~\n%s' % BOTTOMHELPFULL
		dba.add_object(tb_message, {
	  							'userid':user,
	  							'message':msg,
	  							'type':'error',
	  							'typeid': MESSAGE_TYPE_ERROR,
	  							'dir':MESSAGE_DIR_INTER,
	  							'time':int(time())
	  							}
	  				)
	msgobj = None
	if type(rets) != type((1,)):
		msgobj = {	'userid':user,
					'message':rets,
					'type':'text(%s)' % (entm - sttm),
					'typeid': MESSAGE_TYPE_TEXT,
					'dir':MESSAGE_DIR_DOWN,
					'time':int(time())
					}
	else:
		msgobj = {	'userid':user,
					'message':rets[1],
					'type':'%s(%s)' % (rets[0] == MESSAGE_TYPE_IMAGE and 'image' or 'unknow', (entm - sttm)),
					'typeid': MESSAGE_TYPE_IMAGE,
					'dir':MESSAGE_DIR_DOWN,
					'time':int(time())
					}
	dba.add_object(tb_message, msgobj)
	ctx.msgobj = msgobj
	return rets

def whensubscribeevent(user, ctype='weixin', ctx=None):
	'''
	用户订阅
	'''
	dba = ctx.dba
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

def whenunsubscribeevent(user, ctype='weixin', ctx=None):
	'''
	用户取消订阅
	'''
	dba = ctx.dba
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
	while True:
		msg = raw_input('')
		if len(msg) > 0:
			print handlemessage('user', msg)










