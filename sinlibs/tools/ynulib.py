# -*- coding: UTF-8 -*
'''
Created on 2013-9-13

@author: RobinTang
'''

import re
import urllib2
from xml.dom import minidom
from sinlibs.utils import strings
import sys
reload(sys)
try:
    sys.setdefaultencoding("utf-8")
except:
    pass
def search_books(keyword, way="title", page=1):
    url = 'http://202.203.222.211/opac/search?rows=30&&q=%s&searchWay=%s&page=%s' % (keyword, way, page)
    print url
    html = urllib2.urlopen(url).read()
    table = strings.strbetween(html, '<table class="resultTable">', '</table>', contain=True)
    starti = 0
    books = {}
    while True and table != None:
        rg = strings.strbetweenrange(table, '<tr>', '</tr>', starti=starti, contain=True)
        if rg:
            ihtm = table[rg[0]:rg[1]]
            res = re.findall('<span class="bookmetaTitle">\s*<a href="[^"]*" id="title_([^"]*)">\s*([^<]*)\s*</a>', ihtm, re.IGNORECASE | re.MULTILINE)
            bookid = res[0][0].strip()
            name = res[0][1].strip()
            books[bookid] = {'bookid':bookid, 'name':name, 'index':''}
            starti = rg[1] + 1
        else:
            break
    
    url = 'http://202.203.222.211/opac/book/callnos?bookrecnos=%s' % (','.join(books.keys()))
    xml = urllib2.urlopen(url).read()
    doc = minidom.parseString(xml)
    for cld in doc.childNodes[0].childNodes:
        try:
            books[str(cld.childNodes[0].firstChild.data)]['index'] = str(cld.childNodes[1].firstChild.data)
        except:
            pass
    return [x for x in books.values()]
if __name__ == '__main__':
    books = search_books('科学')
    print '\n'.join(['%s(%s)' % (book['name'], book['index']) for book in books])





