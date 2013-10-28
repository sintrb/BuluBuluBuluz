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
# 	print keyword
# 	keyword = urllib2.quote(keyword.encode('gbk'))
	url = 'http://202.203.222.211/opac/search?rows=30&&q=%s&searchWay=%s&page=%s' % (keyword, way, page)
	try:
		html = urllib2.urlopen(url).read()
	except urllib2.HTTPError:
		return []
	except:
		return None
	
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
	if len(books) == 0:
		return []
	
	url = 'http://202.203.222.211/opac/book/callnos?bookrecnos=%s' % (','.join(books.keys()))
	try:
		xml = urllib2.urlopen(url).read()
	except:
		return None
	doc = minidom.parseString(xml)
	for cld in doc.childNodes[0].childNodes:
		try:
			books[str(cld.childNodes[0].firstChild.data)]['index'] = str(cld.childNodes[1].firstChild.data)
		except:
			pass
	return [x for x in books.values()]


def get_holdinginfo(bookid):
	url = 'http://202.203.222.211/opac/book/holdingpreview/%s' % bookid
	try:
		xml = urllib2.urlopen(url).read()
	except:
		return None
	doc = minidom.parseString(xml)
	holds = []
	for cld in doc.childNodes[0].childNodes:
		try:
			holds.append({'libname':str(cld.childNodes[2].firstChild.data),
						'locname':str(cld.childNodes[4].firstChild.data),
						'number':str(cld.childNodes[5].firstChild.data)})
		except:
			pass
	return holds
if __name__ == '__main__':
	import types
	books = search_books(r'在坚持自己了解')
	if type(books) is types.ListType:
		if books:
			print 'ct:%d'%len(books)
# 			for book in books:
# 				print book['name']
		else:
			print 'empty'
	else:
		print 'fail'





