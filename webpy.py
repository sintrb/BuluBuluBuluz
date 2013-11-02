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

import traceback
import hashlib

web.config.debug = True

render = web.template.render('templates/')
web.render = render

urls = (
		'/api', 'WeiXinAPI',
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

class WeiXinAPI(BubulBase):		
	def GET(self):
		try:
			web.header('Content-Type', 'text/xml; charset=utf-8')
			data = web.data()
			return wxhandler.process_request(parameters=web.input(), postdata=data, context=self.ctx)
		except:
			web.header('Content-Type', 'text/html; charset=utf-8')
# 			print 'fail. xml: %s' % web.data()
# 			print '-------------------------'
			errinfo = traceback.format_exc()
			print errinfo
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
		if not web.cookies().get('usertoken'):
			usertk = hashlib.sha1(gentoken(l=20)).hexdigest()
			web.setcookie('usertoken', usertk, 3600 * 24 * 365)
			user = usertk
			whensubscribeevent(usertk, 'web', self.ctx)
		else:
			user = web.cookies().get('usertoken')
		msg = web.input(message='?').message
		ret = {
			   'status': True,
			   'message': handlemessage(user, msg, self.ctx)
			   }
		return json.dumps(ret)

app = web.application(urls, globals())

if __name__ == "__main__":
	app.run()


