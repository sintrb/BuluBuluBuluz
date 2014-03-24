# -*- coding: UTF-8 -*
'''
Created on 2013-9-28

@author: RobinTang
@see: https://github.com/sintrb/SinLikeTerminal



Design doc.

message
?	# current function help
>?	# current function help
>a	# set current function with a

xx	# process message with current function
#?	# global help
#a.b.c	# process message with global function


'''

import sys
try:
	reload(sys)
	sys.setdefaultencoding("utf-8")
except:
	pass

class PrefixDict(object):
	'''
	A Dictionary Adapter.
	It can be use as a Dictionary.
	It's implemented by a normal Dictionary witch can be share for many PrefixDict.
	Such as:
	-   rawdict = {}
	-   user1 = PrefixDict(rawdict=rawdict, prefix='u1')
	-   user2 = PrefixDict(rawdict=rawdict, prefix='u2')
	-   user3 = PrefixDict(rawdict=rawdict, prefix='u3')
	-   user1['name'] = 'User1'
	-   user2['name'] = 'User2'
	-   user3['name'] = 'User3'
	-   print user1['name']
	-   print user2['name']
	-   print user3['name']
	'''
	def __init__(self, rawdict={}, prefix=''):
		self.rawdict = rawdict
		self.prex = prefix
	def __trankey__(self, key):
		return '%s_%s' % (self.prex, key)
	
	# Implement Dictionary function
	def __getitem__(self, key):
		return self.rawdict.__getitem__(self.__trankey__(key))
	def __setitem__(self, key, value):
		return self.rawdict.__setitem__(self.__trankey__(key), value)
	def __delitem__(self, key):
		return self.rawdict.__delitem__(self.__trankey__(key))
	def __contains__(self, key):
		return self.rawdict.__contains__(self.__trankey__(key))
	def __str__(self):
		return self.rawdict.__str__()


def SLTAddAttrs(**kwds):
	def decorate(c):
		for k in kwds:
			setattr(c, k, kwds[k])
		return c
	return decorate


@SLTAddAttrs(name='func1', help='help1')
def func1(uid, msg, sesn, ctx):
	return 'func1 %s' % msg

@SLTAddAttrs(name='func2', help='help2')
def func2(uid, msg, sesn, ctx):
	return 'func2 %s' % msg

@SLTAddAttrs(name='func3', help='help3')
def func3(uid, msg, sesn, ctx):
	return 'func3 %s' % msg

@SLTAddAttrs(name='func4', help='help4')
def func4(uid, msg, sesn, ctx):
	return 'func4 %s' % msg

class SinLikeTerminal():
	'''
	A chat robot Terminal
	'''
	__PREFIX_CURRENT__ = '>'
	__PREFIX_GLOBAL__ = '#'
	__PREFIX_BACK__ = '<'
	
	__PREFIXS__ = [__PREFIX_CURRENT__, __PREFIX_GLOBAL__]
	
	
	__LINE_SPLIT__ = '----------'
	
	__CHAR_HELP__ = '?'
	__ROUTE_SPLIT__ = '.'
	__USER_ROUTE__ = 'route'
	
	def __init__(self, sessinstore={}, route=None, debug=False):
		self.session = sessinstore
		self.route_list = []
		self.route = route
		self.debug = debug
	
	def __get_current_routes__(self, usersession):
		return None if not SinLikeTerminal.__USER_ROUTE__ in usersession else usersession[SinLikeTerminal.__USER_ROUTE__]
	
	def __set_current_routes__(self, usersession, routes):
		usersession[SinLikeTerminal.__USER_ROUTE__] = routes
		
	def __get_route__(self, usersession, routes):
		if routes:
			rt = self.route
			rts = []
			for k in routes.split(SinLikeTerminal.__ROUTE_SPLIT__):
				if 'subfunc' in rt and k in rt['subfunc']:
					rt = rt['subfunc'][k]
					rts.append(k)
				else:
					break
			rt['route'] = SinLikeTerminal.__ROUTE_SPLIT__.join(rts)
			return rt
		else:
			self.route['route'] = ''
			return self.route
	
	def __get_current_route__(self, usersession):
		route = self.__get_route__(usersession, self.__get_current_routes__(usersession))
		self.__set_current_routes__(usersession, route['route'])
		return route
		
	
	def __process_message_with_route__(self, route, message, uid, usersession, context):
		return route(uid, message, usersession, context)
	
	def process_message(self, uid, message, context):
		usersession = PrefixDict(rawdict=self.session, prefix=str(uid))
		if self.debug:
			print self.__get_current_routes__(usersession)
		if message[0] == SinLikeTerminal.__PREFIX_BACK__:
			# back
			routes = self.__get_current_routes__(usersession)
			if routes.rfind(SinLikeTerminal.__ROUTE_SPLIT__) > 0:
				self.__set_current_routes__(usersession, routes[0:routes.rfind(SinLikeTerminal.__ROUTE_SPLIT__)])
			else:
				self.__set_current_routes__(usersession, None)
			route = self.__get_current_route__(usersession)
			return self.__gen_help__(route)
		if message[0] == SinLikeTerminal.__PREFIX_CURRENT__:
			# current message process
			route = self.__get_current_route__(usersession)
			nrs = message[1:]
			if 'subfunc' in route and nrs in route['subfunc']:
				routes = nrs if not len(route['route']) else '%s%s%s' % (route['route'], SinLikeTerminal.__ROUTE_SPLIT__, nrs)
				self.__set_current_routes__(usersession, routes)
				route = self.__get_current_route__(usersession)
				return self.__gen_help__(route)
			else:
				return 'fail'
		elif message[0] == SinLikeTerminal.__PREFIX_GLOBAL__:
			if message[1] == SinLikeTerminal.__CHAR_HELP__:
				# global help
				return self.__gen_help__(route)
		else:
			route = self.__get_current_route__(usersession)
			if message == SinLikeTerminal.__CHAR_HELP__:
				# current help
				return self.__gen_help__(route)
			else:
				return self.__process_message_with_route__(route['func'], message, uid, usersession, context)

	def __gen_help__(self, route):
		if 'subfunc' in route and len(route['subfunc']) and len(route['help'])==0:
			return route['funcs']
		else:
			return route['help']
		
	def add_route(self, route, func):
		'''
		Add a route to Terminal
		'''
		self.route_list.append({'route':route, 'name':func.name, 'func':func, 'help':func.help})
	
	def refresh_allroute(self):
		'''
		Refresh all route dictionary.
		'''
		route = {}
		for rt in self.route_list:
			rts = rt['route']
			rtss = rts.split(SinLikeTerminal.__ROUTE_SPLIT__)
			crt = route
			if len(rtss) > 1:
				del rtss[0]
				for s in rtss:
					if not 'subfunc' in crt:
						crt['subfunc'] = {}
					if not s in crt['subfunc']:
						crt['subfunc'][s] = {} 
					crt = crt['subfunc'][s]
			crt['name'] = rt['name']
			crt['func'] = rt['func']
			crt['help'] = rt['help']
			crt['id'] = rtss[-1]
		del self.route
		self.route = route
		self.refresh_route(self.route)

	def refresh_route(self, route):
		'''
		Refresh single route dictionary.
		'''
		if 'subfunc' in route and len(route['subfunc']):
			chls = []
			for ch in route['subfunc'].values():
				chls.append('%s%s %s' % (SinLikeTerminal.__PREFIX_CURRENT__, ch['id'], ch['name']))
			route['funcs'] = '%s\n%s\n%s' % (route['name'], SinLikeTerminal.__LINE_SPLIT__, '\n'.join(chls))
			for ch in route['subfunc'].values():
				self.refresh_route(ch)

if __name__ == '__main__':
	slt = SinLikeTerminal(route={})
	slt.add_route('r1', func1)
	slt.add_route('r1.r2', func2)
	slt.add_route('r1.r2.r3', func3)
	slt.add_route('r1.r4', func4)
	slt.refresh_allroute()
	sessionid = 'trb'
	while True:
		ins = raw_input("input: ")
		if len(ins) > 0:
			print slt.process_message(sessionid, ins, None)
	print slt.route
	
	
	
	
	
	
	
	
