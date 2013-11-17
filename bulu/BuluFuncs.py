# -*- coding: UTF-8 -*
'''
Created on 2013-10-5

@author: RobinTang
'''

from sinlibs.tools.ynulib import search_books, get_holdinginfo
from SinLikeTerminal import SLTAddAttrs, PrefixDict
from sinlibs.db.SinKVDB import SinKVDB
import Bulu
import types
SPLITLINE = '-----------'
LONGSPLITLINE = '%s%s'%(SPLITLINE, SPLITLINE)
BOTTOMHELP = '你可以发送问号(?)给我'
BOTTOMHELPFULL = '%s\n%s' % (LONGSPLITLINE, BOTTOMHELP)

def is_num(s):
	try:
		int(s)
		return True
	except:
		return False

@SLTAddAttrs(name='图书馆搜索', help='目前支持云大图书搜索.\n告诉我书名或关键字即可.\n如果我没有回应你可以尝试再发发送.\n网页版<a href="http://bulubulubuluz.sinaapp.com/">BuluBuluBuluz</a>')
def ynu_lib_search(user, msg, sesn, ctx=None):
	rows = 20
	ynu_lib_ser_err = 'Oops...\n联系不到图书馆服务器~\n%s'%BOTTOMHELPFULL
	keyword = msg.strip()
	rets = '抱歉~~\n没有找到相关图书.\n目前只支持单关键字,\n请试着简化一下关键字.\n%s'%BOTTOMHELPFULL
	if len(keyword) > 0:
		sesn = PrefixDict(rawdict=sesn, prefix='ynu_lib_search')
		page = 1
		if keyword in 'nN':
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
			stbks = sesn['books']
			if stbks and ix >= 0 and ix <len(stbks):
				bk = stbks[ix]
				holds = get_holdinginfo(bk['bookid'])
				if holds:
					spl = '\n%s\n' % SPLITLINE
					hds = spl.join(['馆名:%s\n位置:%s\n数目:%s'%(hd['libname'], hd['locname'], hd['number']) for hd in holds])
					info = '%s\n索引号:%s'%(bk['name'], bk['index'])
					rets = '%s\n%s\n%s\n%s\n%s'%(info, LONGSPLITLINE, hds, LONGSPLITLINE, '输入数字继续许查看明细')
				else:
					rets = ynu_lib_ser_err
			else:
				spl = '\n%s\n' % SPLITLINE
				bks = spl.join(['%d. %s (%s)' % (ix, stbks[ix]['name'], stbks[ix]['index']) for ix in range(len(stbks))])
				return '输入的数字超出了范围!\n%s\n%s\n%s\n%s'%(LONGSPLITLINE, bks, LONGSPLITLINE, '输入数字查看明细')
		else:
			sesn['keyword'] = keyword
			
			searchkey='%s_r%s_p%s'%(keyword, rows, page)
			searchkvdb = SinKVDB(ctx.con, table='tb_bulu_kvdb_ynusch', tag='bulu', cache=False, debug=False, create=False)
			if searchkey in searchkvdb:
				books = searchkvdb[searchkey]
			else:
				books = search_books(keyword=keyword, page=page, rows=rows)
				if type(books) is types.ListType:
					searchkvdb[searchkey] = books
			if type(books) is types.ListType:
				ixs = []
				bmp = {}
				for book in books:
					if book['index'] and len(book['index']):
						ixs.append(book['index'])
						bmp[book['index']] = book
				if len(ixs):
					ixs.sort()
					spl = '\n%s\n' % SPLITLINE
					stbks = [bmp[ix] for ix in ixs]
					bks = spl.join(['%d. %s (%s)' % (ix, stbks[ix]['name'], stbks[ix]['index']) for ix in range(len(stbks))])
					sesn['books'] = stbks
					htip = '数字看明细'
					pgt = '第%s页 N下页  '%page
					if page>1:
						pgt = '%sP上页\n'%pgt
					pgt = '%s%s'%(pgt, htip)
					rets = '%s :%d条\n%s\n%s\n%s\n%s' % (keyword, len(ixs), LONGSPLITLINE, bks, LONGSPLITLINE, pgt)
					sesn['page'] = page
				elif page != 1:
					rets = '%s :没有了\n%s\n第%s页  P上一页' % (keyword, LONGSPLITLINE, page)
				else:
					rets = '%s\n抱歉~~\n没有找到相关图书.\n目前只支持单关键字,\n请试着简化一下关键字.\n%s'%(keyword, BOTTOMHELPFULL)
			else:
				rets = ynu_lib_ser_err
	return rets


@SLTAddAttrs(name='echo', help='回显测试\n给我消息我原样返回')
def tool_echo(user, msg, sesn, ctx=None):
	return msg

@SLTAddAttrs(name='调试', help='调试模式,支持:\n who\n stc')
def tool_debug(user, msg, sesn, ctx=None):
	if msg == 'who':
		return str(user)
	if msg == 'stc':
		from sinlibs.db.dbbase import get_connect
		from sinlibs.db.SinDBAccess import SinDBAccess
		from Bulu import tb_event, tb_message
		dbcon = get_connect()
		dba = SinDBAccess(dbcon, debug=False)
		count = dba.get_count(tb_event)
		sub = dba.get_count(tb_event, conditions={'eventid':1})
		unsub = dba.get_count(tb_event, conditions={'eventid':2})
		mcount = dba.get_count(tb_message, conditions={'dir':1})
		return '订阅: %s\n退订: %s\n剩余: %s\n总数: %s\n\n消息:%s'%(sub, unsub, sub-unsub, count, mcount)
	return 'unkown'

@SLTAddAttrs(name='设置模式', help='设置模式\nkey=value')
def tool_config(user, msg, sesn, ctx=None):
	if msg == 'show':
		ss = ['%s=%s'%(k, v) for (k,v) in Bulu.config.items()]
		return '\n'.join(ss)
	
	kvs = msg.split('=')
	if len(kvs)==2:
		k = kvs[0].strip()
		v = eval(kvs[1].strip())
		Bulu.config[k] = v
		ss = ['%s=%s'%(k, v) for (k,v) in Bulu.config.items()]
		return '\n'.join(ss)
	return 'unkown'


