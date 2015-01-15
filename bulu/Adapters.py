# -*- coding: UTF-8 -*
'''
Created on 2015年1月14日

@author: RobinTang
'''

class BaseAdapter:
    def text(self, txt):
        raise Exception("unimplemented")
    def image(self, img):
        raise Exception("unimplemented")
    def article(self, title, desc, imgurl, url):
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
    def article(self, title, desc, imgurl, url):
        Article = {
                   'Title':title,
                   'Description':desc,
                   'PicUrl':imgurl,
                   'Url':url
                   }
        return self.wxaccess.response_articlesmsg([Article, ])
class WebAdapter(BaseAdapter):
    def text(self, txt):
        return txt
    def image(self, imgurl):
        return '<img src="%s" />' % imgurl
    def article(self, title, desc, imgurl, url):
        import cgi
        return '<h3><a href="%s">%s</a></h3> <img src="%s" /><p>%s</p>' % (url, cgi.escape(title), imgurl, cgi.escape(desc))



