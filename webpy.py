# -*- coding: UTF-8 -*
'''
Created on 2013-8-31

@author: RobinTang
'''

import web
import json
from Handlers import TencentWX 
from bulu.Bulu import handlemessage
from sinlibs.utils.strings import gentoken
from sinlibs.db.dbbase import get_connect
from bulu.Bulu import whensubscribeevent

from sinlibs.db.SinDBAccess import SinDBAccess
from sinlibs.db.SinKVDB import SinKVDB
from bulu.Bulu import tb_message, MESSAGE_TYPE_TEXT, MESSAGE_DIR_DOWN
from bulu.Adapters import BaseAdapter, WebAdapter
from auto.AutoTest import runtest

import traceback
import hashlib
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
web.config.debug = True

web.config.smtp_server = 'smtp.163.com'
web.config.smtp_port = 25
web.config.smtp_username = 'itsjustamail@163.com'
web.config.smtp_password = 'justamail'
web.config.smtp_starttls = True


render = web.template.render('templates/')
web.render = render

urls = (
		'/api', 'WeiXinAPI',
		'/autotest', 'AutoTest',
		'/showmsg/([^/]*)/([^/]*)', 'ShowMsg',
		'/([^/]*.ico)', 'StaticFile',
		'.*', 'OnlineBulu',
)


wxhandler = TencentWX()


class Context():
	pass


class BubulBase():
	def __init__(self):
		self.ctx = Context()
		self.ctx.con = get_connect()
		self.ctx.dba = SinDBAccess(self.ctx.con, debug=False)
		self.ctx.kvdb = SinKVDB(self.ctx.con, table='tb_bulu_kvdb', tag='bulu', cache=False, debug=False, create=True)

class ShowMsg(BubulBase):
	def GET(self, userid, times):
		res = self.ctx.dba.get_objects(tb_message, columns='message', conditions={'userid':userid, 'time':times, 'typeid': MESSAGE_TYPE_TEXT, 'dir':MESSAGE_DIR_DOWN}, condtype='and', limit=1, order='id desc')
		if res and len(res):
			lmsg = res[0]['message']
			kvdb = SinKVDB(self.ctx.con, table='tb_bulu_kvdb_showmsg', tag='bulu', cache=False, debug=False, create=True)
			ct = 0
			ky = 'count_%s_%s' % (userid, times)
			try:
				ct = int(kvdb[ky])
			except:
				pass
			ct = ct + 1
			kvdb[ky] = ct
			return render.showmsg(msg=lmsg.replace('\n', '<br />'), count=ct)
# 			return lmsg
		else:
			return render.showmsg(msg='消息不存在或者已经过期~', count='o0O@')

class WeiXinAPI(BubulBase):
	def GET(self):
		try:
			web.header('Content-Type', 'text/xml; charset=utf-8')
			data = web.data()
# 			remsg = 
			return wxhandler.process_request(parameters=web.input(), postdata=data, context=self.ctx)
		except:
			web.header('Content-Type', 'text/html; charset=utf-8')
# 			print 'fail. xml: %s' % web.data()
# 			print '-------------------------'
# 			errinfo = traceback.format_exc()
# 			print errinfo
		return render.errorequest()
	def POST(self):
		return self.GET()

class StaticFile:
	def GET(self, staticfile):
		print 'get static:', staticfile
		web.seeother('/static/' + staticfile, False)

class OnlineBulu(BubulBase):
	def GET(self):
		web.header('Content-Type', 'text/html; charset=utf-8')
		return render.onlinebulu()
	def POST(self):
		self.ctx.adapter = WebAdapter()
		if not web.cookies().get('usertoken'):
			usertk = hashlib.sha1(gentoken(l=20)).hexdigest()
			web.setcookie('usertoken', usertk, 3600 * 24 * 365)
			user = usertk
			whensubscribeevent(usertk, 'web', self.ctx)
		else:
			user = web.cookies().get('usertoken')
		msg = web.input(message='?').message
		res = handlemessage(user, msg, self.ctx)
		ret = {
			   'status': True,
			   'message': res if type(res) != type((0,)) else res[1]
			   }
		return json.dumps(ret)

class AutoTest():
	def __init__(self):
		self.kvdb = SinKVDB(get_connect(), table='tb_bulu_kvdb_autotest', tag='bulu', cache=True, debug=False, create=True)
	def GET(self):
		return runtest(self.kvdb)

app = web.application(urls, globals())

if __name__ == "__main__":
	app.run()


