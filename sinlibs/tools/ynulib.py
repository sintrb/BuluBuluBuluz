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

def get_seachurl(keyword, way="title", page=1, rows=20):
	kws = [kw for kw in keyword.split() if len(kw) > 0]
	if len(kws) == 1:
		return 'http://202.203.222.211/opac/search?rows=%s&q=%s&searchWay=%s&page=%s' % (rows, kws[0], way, page)
	else:
		qa = []
		for i in range(len(kws)):
			kw = kws[i].strip()
			qa.append('searchWay%d=title&q%d=%s&logical%d=OR' % (i, i, kw, i))
		qs = '&'.join(qa)
		return 'http://202.203.222.211/opac/search?&searchSource=reader&inside=&booktype=&marcformat=&sortWay=score&sortOrder=desc&startPubdate=&endPubdate=&rows=%s&page=%s&hasholding=1&%s' % (rows, page, qs)
	
def get_html(url):
	req = urllib2.Request(url)
	req.add_header('Referer', 'http://202.203.222.211/opac/index')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0')
	return urllib2.urlopen(req).read()

def search_books(keyword, way="", page=1, rows=20):
# 	print keyword
# 	keyword = urllib2.quote(keyword.encode('gbk'))
	keyword = keyword.strip()
	url = get_seachurl(keyword, way, page, rows)
	print url
	try:
		html = get_html(url)
	except:
		return None
# 	print html
	table = strings.strbetween(html, '<table class="resultTable">', '</table>', contain=True)
	starti = 0
	books = {}
	allbooks = []
	while True and table != None:
		rg = strings.strbetweenrange(table, '<tr>', '</tr>', starti=starti, contain=True)
		if rg:
			try:
				ihtm = table[rg[0]:rg[1]]
				# 1.0
				# patn = '<span class="bookmetaTitle">\s*<a href="[^"]*" id="title_([^"]*)">\s*([^<]*)\s*</a>'
				
				# 1.1 2014-04-09
				patn = '<span class="bookmetaTitle">\s*<a href="[^"]*" id="title_([^"]*)"[^/]*>\s*([^<]*)\s*</a>'
				res = re.findall(patn, ihtm, re.IGNORECASE | re.MULTILINE)
				bookid = res[0][0].strip()
				name = res[0][1].strip().strip(' /')
				
				book = {'bookid':bookid, 'name':name, 'index':''}
				try:
					book['author'] = re.findall("searchWay=author&q=([^\"]+)", ihtm)[0]
				except:
					pass
				try:
					book['isbn'] = re.findall('isbn="([^"]*)"', ihtm)[0]
				except:
					pass
				books[bookid] = book
				allbooks.append(book)
			except:
				print 'error'
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
	return allbooks


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

def get_bookinfo_by_isbn(isbns):
	if type(isbns) == type([]):
		isbns = ','.join(isbns)
	isbns = isbns.replace('-', '')
	url = 'http://api.interlib.com.cn/interlibopac/websearch/metares?cmdACT=getImages&type=0&callback=S&isbns=%s' % isbns
	print get_html(url)

def togbk(us):
	return us

def test(k="Java"):
	import types
	books = search_books(k)
	if type(books) is types.ListType:
		if books:
			print 'ct:%d' % len(books)
			for book in books:
				print '%s %s' % (book['name'], book)
		else:
			print 'empty'
	else:
		print 'fail'

if __name__ == '__main__':
	test('图像融合')
# 	get_bookinfo_by_isbn('978-7-5641-4659-7')





