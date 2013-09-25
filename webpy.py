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

class WeiXinAPI(object):
    def GET(self):
        try:
            web.header('Content-Type', 'text/xml; charset=utf-8')
            return wxhandler.process_request(parameters=web.input(), postdata=web.data())
        except:
            web.header('Content-Type', 'text/html; charset=utf-8')
            print 'fail xml: %s'%web.data()
            return render.errorequest()
    def POST(self):
        return self.GET()

class StaticFile:
    def GET(self, staticfile):
        print 'get static:', staticfile
        web.seeother('/static/' + staticfile, False)

class OnlineBulu(object):
    def GET(self):
        if not web.cookies().get('usertoken'):
            usertk = hashlib.sha1(gentoken(l=20)).hexdigest()
            web.setcookie('usertoken', usertk, 3600*24*365)
        web.header('Content-Type', 'text/html; charset=utf-8')
        return render.onlinebulu()
    def POST(self):
        msg = web.input(message='?').message
        ret = {
               'status': True,
               'message': handlemessage(web.cookies().get('usertoken'), msg)
               }
        return json.dumps(ret)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()


