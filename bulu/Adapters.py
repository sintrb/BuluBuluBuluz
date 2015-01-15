# -*- coding: UTF-8 -*
'''
Created on 2015年1月14日

@author: RobinTang
'''

class BaseAdapter:
    TYPE_TEXT = 0
    TYPE_IMAGE = 1
    def text(self, txt):
        raise Exception("unimplemented")
    def image(self, img):
        raise Exception("unimplemented")

class WXAdapter(BaseAdapter):
    def __init__(self, wxaccess):
        self.wxaccess = wxaccess
    def text(self, txt):
        return self.wxaccess.response_textmessage(txt)
    def image(self, imgurl):
        Article = {
                   'Title':'图片',
                   'Description':'图片描述',
                   'PicUrl':imgurl,
                   'Url':imgurl
                   }
        return self.wxaccess.response_articlesmsg([Article, ])

class WebAdapter(BaseAdapter):
    def text(self, txt):
        return txt
    def image(self, imgurl):
        return '<img src="%s" />' % imgurl



