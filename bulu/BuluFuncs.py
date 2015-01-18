# -*- coding: UTF-8 -*
'''
Created on 2013-10-5

@author: RobinTang
'''
import sinlibs

SPLITLINE = '-----------'
LONGSPLITLINE = '%s%s' % (SPLITLINE, SPLITLINE)
BOTTOMHELP = '你可以发送问号(?)给我'
BOTTOMHELPFULL = '%s\n%s' % (LONGSPLITLINE, BOTTOMHELP)

from sinlibs.tools.ynulib import search_books, get_holdinginfo, get_douban_book_by_isbn
from SinLikeTerminal import SLTAddAttrs, PrefixDict
from sinlibs.db.SinKVDB import SinKVDB
from sinlibs.db.SinDBAccess import SinDBAccess
import Bulu
import types
import time


def is_num(s):
	try:
		int(s)
		return True
	except:
		return False

def books_to_lines(books):
	return ['%d. %s - %s (%s)' % (ix + 1, books[ix]['name'], 'author' in books[ix] and books[ix]['author'], books[ix]['index']) for ix in range(len(books))]


@SLTAddAttrs(name='图书馆搜索', help='目前支持云大图书搜索.\n告诉我书名或关键词即可,多个关键词之间用空格隔开.\n如果我长时间没能回应你可以尝试再发发送.\n网页版<a href="http://bulubulubuluz.sinaapp.com/">BuluBuluBuluz</a>')
def ynu_lib_search(user, msg, sesn, ctx=None):
	rows = 20
	usecache = True
	ynu_lib_ser_err = 'Oops...\n联系不到图书馆服务器~\n%s' % BOTTOMHELPFULL
	keyword = msg.strip()
	rets = '%s\n抱歉~~\n没有找到相关图书.\n请试着简化一下关键字,并使用空格将关键字隔开.\n%s' % (keyword, BOTTOMHELPFULL)
	if len(keyword) > 0:
		sesn = PrefixDict(rawdict=sesn, prefix='ynu_lib_search')
		page = 1
		if keyword in 'dD' and sesn['book']:
# 			PrefixDict(rawdict=ctx.kvdb, prefix='ynu_lib_bookinfo_by_isbn')
			try:
				book = sesn['book']
				if 'isbn' in book and  book['isbn']:
					infokey = 'douban_book_info_%s' % (book['isbn'])
					info = ctx.kvdb.get_value_after(infokey, time.time() - 60 * 60)
					flag = False
					if not info:
						info = get_douban_book_by_isbn(book['isbn'])
						flag = True
					if info and ('code' not in info or not info['code']):
						if flag:
							ctx.kvdb[infokey] = info
						p = '%s(豆瓣)' % info['summary']
						t = '%s %s' % (info['title'], info['rating']['average'])
						img = 'http://urlimg.sinaapp.com/?url=%s&width=360&height=200' % info['images']['medium']
# 						img = 'http://172.16.0.102:9999/?url=%s' % info['images']['medium']
						return (Bulu.MESSAGE_TYPE_IMAGE, ctx.adapter.article(t, p, img, info['alt']))
					else:
						return '查询豆瓣接口失败'
				else:
					return '没有ISBN码的书籍无法查询'
			except:
				return '抱歉~~~查询的时候出了些问题~'
				
		elif keyword in 'nN':
			# next page
			try:
				if 'page' in sesn:
					page = sesn['page'] + 1
				else:
					page = 1
			except:
				page = 1
			keyword = sesn['keyword']
		elif keyword in 'pP':
			# pre page
			try:
				if 'page' in sesn:
					page = sesn['page'] - 1
				else:
					page = 1
			except:
				page = 1
			if page <= 0:
				page = 1
			keyword = sesn['keyword']
		
		if is_num(keyword) and sesn['books']:
			ix = int(keyword)
			books = sesn['books']
			if ix >= 0 and ix <= len(books):
				if ix == 0:
					return '只有程序员才从0开始数数~，你不会是程序员吧'
				else:
					bk = books[ix - 1]
					holds = get_holdinginfo(bk['bookid'])
					if holds != None:
						spl = '\n%s\n' % SPLITLINE
						if holds:
							hds = spl.join(['馆名:%s\n位置:%s\n数目:%s' % (hd['libname'], hd['locname'], hd['number']) for hd in holds])
						else:
							hds = '没有查找到在馆信息'
						info = '%s\n索引号:%s' % (bk['name'], bk['index'])
						bottomtip = '输入其他数字查看对应图书明细'
						if 'isbn' in bk and bk['isbn']:
							info = '%s\nISBN:%s' % (info, bk['isbn'])
							bottomtip = '%s\n%s' % ('D在豆瓣上查看该图书信息', bottomtip)
						sesn['book'] = bk
						rets = '%s\n%s\n%s\n%s\n%s' % (info, LONGSPLITLINE, hds, LONGSPLITLINE, bottomtip)
					else:
						rets = ynu_lib_ser_err
			else:
				spl = '\n%s\n' % SPLITLINE
				bks = spl.join(books_to_lines(books))
				return '输入的数字超出了范围!\n%s\n%s\n%s\n%s' % (LONGSPLITLINE, bks, LONGSPLITLINE, '输入数字查看明细')
		else:
			sesn['keyword'] = keyword
			
			searchkey = '%s_r%s_p%s' % (keyword, rows, page)
			searchkvdb = SinKVDB(ctx.con, table='tb_bulu_kvdb_ynusch', tag='bulu', cache=False, debug=False, create=True)
			books = None
			iscache = False
			if usecache and searchkey in searchkvdb:
				try:
					modifytime = searchkvdb.get_one(searchkey)['modifytime']
					if (time.time() - modifytime) < (3600 * 24):
						# 缓存一天
						books = searchkvdb[searchkey]
						iscache = True
				except:
					print 'error'
					pass
			if not books:
				books = search_books(keyword=keyword, page=page, rows=rows)
				if type(books) is types.ListType:
					searchkvdb[searchkey] = books
			elif type(books) is types.ListType:
				books = [b for b in books if b['index']]
			if type(books) is types.ListType:
				if len(books):
					spl = '\n%s\n' % SPLITLINE
					bks = spl.join(['%d. %s - %s (%s)' % (ix + 1, books[ix]['name'], 'author' in books[ix] and books[ix]['author'], books[ix]['index']) for ix in range(len(books))])
					sesn['books'] = books
					htip = '输入数字看图书明细'
					pgt = '第%s页 N下页  ' % page
					if page > 1:
						pgt = '%sP上页\n' % pgt
					pgt = '%s%s' % (pgt, htip)
					tip = (iscache and '条(来自缓存)') or '条'
					rets = '%s :%d%s\n%s\n%s\n%s\n%s' % (keyword, len(books), tip, LONGSPLITLINE, bks, LONGSPLITLINE, pgt)
					sesn['page'] = page
					if user in ['ofYB4jt9Sk0uIY8tv2nrluSH6jcc', 'ofYB4jns8_E-wvuwrXm2kzHaR-zU']:
						rets = '/:heart%s' % rets  # yeah, the heart is for you
				elif page != 1:
					rets = '%s :没有了\n%s\n第%s页  P上一页' % (keyword, LONGSPLITLINE, page)
				else:
					rets = '%s\n抱歉~~\n没有找到相关图书.\n请试着简化一下关键字,并使用空格将关键字隔开.\n%s' % (keyword, BOTTOMHELPFULL)
			else:
				rets = ynu_lib_ser_err
	return rets


@SLTAddAttrs(name='开发者选项', help='开发者选项')
def tool_dev(user, msg, sesn, ctx=None):
	from  sinlibs.tools import ynulib
	return ynulib.get_html('https://api.douban.com/v2/book/isbn/9787560953489')

@SLTAddAttrs(name='echo', help='回显测试\n给我消息我原样返回')
def tool_echo(user, msg, sesn, ctx=None):
	return msg

@SLTAddAttrs(name='调试', help='调试模式,支持:\n who\n stc\n last')
def tool_debug(user, msg, sesn, ctx=None):
	from Bulu import tb_event, tb_message
	
	sesn = PrefixDict(rawdict=sesn, prefix='debug')
	if msg == 'who':
		return str(user)
	elif msg == 'stc':
		dbcon = ctx.con
		dba = SinDBAccess(dbcon, debug=False)
		count = dba.get_count(tb_event)
		sub = dba.get_count(tb_event, conditions={'eventid':1, 'type':'weixin'})
		unsub = dba.get_count(tb_event, conditions={'eventid':2, 'type':'weixin'})
		mcount = dba.get_count(tb_message, conditions={'dir':1})
		if 'sub' in sesn:
			pres = '新增\n---订阅:%s\n---退订:%s\n---消息:%s\n' % (sub - sesn['sub'], unsub - sesn['unsub'], mcount - sesn['mcount'])
		else:
			pres = ''
		sesn['sub'] = int(sub)
		sesn['unsub'] = int(unsub)
		sesn['count'] = int(count)
		sesn['mcount'] = int(mcount)
		
		return '%s统计\n---订阅: %s\n---退订: %s\n---剩余: %s\n---总数: %s\n---消息:%s' % (pres, sub, unsub, sub - unsub, count, mcount)
	elif msg == 'last':
		from sinlibs.utils.timeutils import stamp2str
		dba = SinDBAccess(ctx.con, debug=False)
		return '\n'.join(['%s %s' % (stamp2str(int(o['time']), '%m-%d %H:%M'), o['message']) for o in dba.get_objects(tb_message, conditions={'dir':1}, order='id desc', limit=15)])
	return 'unkown'

@SLTAddAttrs(name='设置模式', help='设置模式\nkey=value\nshow')
def tool_config(user, msg, sesn, ctx=None):
	if msg == 'show':
		ss = ['%s=%s' % (k, v) for (k, v) in Bulu.config.items()]
		return '\n'.join(ss)
	
	kvs = msg.split('=')
	if len(kvs) == 2:
		k = kvs[0].strip()
		v = eval(kvs[1].replace("(", "").replace(")", "").strip())
		Bulu.config[k] = v
		ss = ['%s=%s' % (k, v) for (k, v) in Bulu.config.items()]
		return '\n'.join(ss)
	return 'unkown'


