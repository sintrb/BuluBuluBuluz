# -*- coding: UTF-8 -*
'''
Created on 2013-9-14

@author: RobinTang
'''


from weixin import WXHandler
from bulu.Bulu import handlemessage, whensubscribeevent, whenunsubscribeevent, BOTTOMHELPFULL


WXTOKEN = 'bulubulubuluztoken'

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
		return wxaccess.response_textmessage(handlemessage(wxaccess.fromuser, wxaccess.get_textmsg()))

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
		return wxaccess.response_textmessage(whensubscribeevent(wxaccess.fromuser))
	
	def whenunsubscribeevent(self, wxaccess):
		'''
		用户取消订阅
		'''
# 		print '--------->unsubscribe: %s' % wxaccess.fromuser
		return wxaccess.response_textmessage(whenunsubscribeevent(wxaccess.fromuser))
	

if __name__ == '__main__':
	WXHandler.test_handler(TencentWX())
