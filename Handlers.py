# -*- coding: UTF-8 -*
'''
Created on 2013-9-14

@author: RobinTang
'''


from weixin import WXHandler
from bulu.Bulu import handlemessage, whensubscribeevent, whenunsubscribeevent, BOTTOMHELPFULL


WXTOKEN = 'bulubulubuluztoken'

WX_TXTMSG_MAXLEN = 2000  # 消息最大长度

class TencentWX(WXHandler):
	'''
	腾讯微信公共平台消息处理
	'''
	def __init__(self, accesstoken=None, wxtoken=None):
		WXHandler.__init__(self, accesstoken=accesstoken, wxtoken=wxtoken or WXTOKEN)
		# 取消对图片、位置、链接、声音、视频的默认处理
		# 删除之后这几种消息都会被当成未知的消息类型
		del self.handlermap['image']
		del self.handlermap['location']
		del self.handlermap['link']
		del self.handlermap['voice']
		del self.handlermap['video']
	
	def whentextmsg(self, wxaccess):
		'''
		文本消息处理
		'''
		# 对于文本消息，调用handlemessage之后放回处理结果
		wxaccess.context.wxaccess = wxaccess
		msg = handlemessage(wxaccess.fromuser, wxaccess.get_textmsg(), wxaccess.context)
		if len(msg.encode("utf-8")) > WX_TXTMSG_MAXLEN:
			# 需要截断
			try:
				bts = msg.encode("utf-8")
				ix = bts.rfind('\n', 0, WX_TXTMSG_MAXLEN - 80)
				if ix > 0:
					rmsg = msg[0:ix]
					msg = '%s\n<a href="http://bulubulubuluz.sinaapp.com/showmsg/%s/%s">显示更多消息...</a>' % (rmsg.decode("utf-8"), wxaccess.fromuser, wxaccess.context.msgobj['time'])
			except:
				pass
		return wxaccess.response_textmessage(msg)

	def whenunknownmsgtype(self, wxaccess):
		'''
		未知消息类型的处理
		'''
		# 图片、语音、位置等信息返回不知道
		return wxaccess.response_textmessage('对不起,主银还没有告诉我怎么理解这类消息~~\n%s' % BOTTOMHELPFULL)
	
	def whensubscribeevent(self, wxaccess):
		'''
		用户订阅
		'''
# 		print '--------->subscribe: %s' % wxaccess.fromuser
		return wxaccess.response_textmessage(whensubscribeevent(wxaccess.fromuser, ctx=wxaccess.context))
	
	def whenunsubscribeevent(self, wxaccess):
		'''
		用户取消订阅
		'''
# 		print '--------->unsubscribe: %s' % wxaccess.fromuser
		return wxaccess.response_textmessage(whenunsubscribeevent(wxaccess.fromuser, ctx=wxaccess.context))
	

if __name__ == '__main__':
	WXHandler.test_handler(TencentWX())
