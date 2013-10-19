# -*- coding: UTF-8 -*
'''
Created on 2013-10-1

@author: RobinTang
@see: https://github.com/sintrb/SinDBAccess
'''

import types


__dbnames__ = ('sqlite', 'mysql', 'postgre')
__TYPE_SQLITE__ = 0
__TYPE_MYSQL__ = 1
__TYPE_PGDB__ = 2


def __ifornot__(e, t, f):
	'''
	A expression like C languege e?:t:f
	Or Python: t if e else f
	'''
	if e:
		return t
	else:
		return f

class SinDBAccess:
	def __init__(self, db, debug=False):
		self.debug = debug
		self.set_db(db)
		self.autocommit = True
		
	def __typemap__(self, v):
		'''
		Mapping Python type with Database type
		'''
		if type(v) is types.StringType:
			if len(v):
				return v
			else:
				return 'text'
		elif type(v) is types.FloatType:
			return __ifornot__(v, 'float not null', 'float')
		elif type(v) is types.IntType:
			return __ifornot__(v, 'int not null', 'int')
		elif type(v) is types.LongType:
			return __ifornot__(v, 'bigint not null', 'bigint')
	
	def __literal__(self, v):
		'''
		Database literal
		'''
		isNone = type(v) is types.NoneType
		if self.__dbtype__ == __TYPE_SQLITE__:
			return "'%s'"%v
		elif self.__dbtype__ == __TYPE_MYSQL__:
			return self.db.literal(v)
		elif self.__dbtype__ == __TYPE_PGDB__:
			return __ifornot__(isNone, 'Null', "'%s'"%v)
	
	
	def __nameliteral__(self, k):
		'''
		Database name literal
		'''
		global __dbtype__
		if self.__dbtype__ == __TYPE_SQLITE__:
			return '`%s`'%k
		elif self.__dbtype__ == __TYPE_MYSQL__:
			return '`%s`'%k
		elif self.__dbtype__ == __TYPE_PGDB__:
			return k
	
	def __createconditions__(self, conditions, condtype):
		'''
		Create conditions by conditions and condition-type
		'''
		if conditions and type(conditions) is types.DictType:
			condtype = ' %s ' % condtype
			conditions = ' where %s'%condtype.join(['%s=%s' % (self.__nameliteral__(k), self.__literal__(v)) for (k, v) in conditions.items()])
		elif conditions:
			conditions = ' where %s' % conditions
		else:
			conditions = ''
		return conditions
	
	def __checkdb__(self, newcur=False):
		'''
		This method use to check the db variable is valid
		'''
		if not self.db:
			raise Exception('The database connection is None. Please open a connection from SinORM before you user the modle')
		if not self.cur or newcur:
			try:
				self.db.ping(True)
			except:
				# pgdb will raise error
				pass
			self.cur = self.db.cursor()
	
	def set_db(self, sdb):
		'''
		Set the database
		'''
		dbtype = str(type(sdb)).lower()
		if dbtype.find('sqlite')>=0:
			# sqlite
			if self.debug:
				print 'sqlite'
			self.__dbtype__ = __TYPE_SQLITE__
		elif dbtype.find('mysql')>=0:
			# MySQL
			if self.debug:
				print 'MySQL'
			self.__dbtype__ = __TYPE_MYSQL__
		elif dbtype.find('pgdb')>=0:
			# PostgreSQL
			if self.debug:
				print 'PostgreSQL'
			self.__dbtype__ = __TYPE_PGDB__
		else:
			raise Exception('Unknown database type:%s'%dbtype)
		self.db = sdb
		self.cur = None
		self.__checkdb__(newcur=True)
	
	def commit(self):
		'''
		Commit the database
		'''
		self.db.commit()
	
	def exe_sql(self, sql, commit=False):
		'''
		Execute a SQL
		'''
		self.__checkdb__()
		if self.debug:
			print '%s sql: %s'%(__dbnames__[self.__dbtype__], sql)
		try:
			res = self.cur.execute(sql)
		except:
			self.__checkdb__(newcur=True)
			res = self.cur.execute(sql)
		if commit:
			self.commit()
		return res
	
	def get_objects_by_sql(self, sql):
		'''
		Get objects from table
		'''
		count = True
		self.exe_sql(sql)
		if count:
			names = [x[0] for x in self.cur.description]
			res = []
			allrow = self.cur.fetchall()
			for row in allrow:
				obj = dict(zip(names, row))
				res.append(obj)
		else:
			res = []
		return res
	
	def get_objects(self, table, columns='*', conditions='', condtype='and', limit='', order='', offset='', group=''):
		'''
		Get objects from table
		'''
		if columns and type(columns) is types.ListType:
			columns = ','.join([self.__nameliteral__(v) for v in columns])
		conditions = self.__createconditions__(conditions, condtype)
		if limit:
			limit = ' limit %s' % limit
		if order:
			order = ' order by %s' % order
		if offset:
			offset = ' offset %s' % offset
		if group:
			group = ' group by %s' % group
		sql = 'select %s from %s%s%s%s%s%s' % (columns, self.__nameliteral__(table), conditions, group, order, limit, offset)
		return self.get_objects_by_sql(sql)
	
	def get_object(self, table, keyid, keyidname='id'):
		'''
		Get one object from table by keyid, keyid is primary-key value, keyidname is primary-key name, default it is "id"
		'''
		sql = 'select * from %s where %s=%s' % (self.__nameliteral__(table), keyidname, self.__literal__(keyid))
		objs = self.get_objects_by_sql(sql)
		if objs:
			return objs[0]
		else:
			return None
		
	def get_count(self, table, conditions='', condtype='and'):
		'''
		Get the count of the table.
		'''
		objs = self.get_objects(table, columns='COUNT(*) as `count`', conditions=conditions, condtype=condtype)
		if objs and len(objs):
			return objs[0]['count']
		else:
			return 0
		

	def set_objects(self, table, obj, conditions='', condtype='and'):
		'''
		Update objects to database by conditions
		'''
		conditions = self.__createconditions__(conditions, condtype)
		setsql = ','.join(['%s=%s' % (self.__nameliteral__(k), self.__literal__(v)) for (k, v) in obj.items()])
		sql = 'update %s set %s%s' % (self.__nameliteral__(table), setsql, conditions)
		return self.exe_sql(sql, self.autocommit)
	
	def set_object(self, table, obj, keyid=0, keyidname='id'):
		'''
		Update a object to database
		'''
		objkeyid = None
		if obj.has_key(keyidname):
			objkeyid = obj[keyidname]
			if not keyid:
				keyid = obj[keyidname]
			del obj[keyidname]	
		conditions = '%s=%s' % (self.__nameliteral__(keyidname), self.__literal__(keyid))
		res = self.set_objects(table, obj, conditions)
		if objkeyid:
			obj[keyidname] = objkeyid
		return res
	
	def del_objects(self, table, conditions='', condtype='and'):
		'''
		Delete objects to database by conditions
		'''
		conditions = self.__createconditions__(conditions, condtype)
		sql = 'delete from %s%s' % (self.__nameliteral__(table), conditions)
		return self.exe_sql(sql, self.autocommit)
	
	def del_object(self, table, obj, keyid=0, keyidname='id'):
		'''
		Delete a object to database by keyid
		'''
		objkeyid = None
		if obj.has_key(keyidname):
			objkeyid = obj[keyidname]
			if not keyid:
				keyid = obj[keyidname]
			del obj[keyidname]	
		conditions = '%s=%s' % (self.__nameliteral__(keyidname), self.__literal__(keyid))
		res = self.del_objects(table, conditions)
		if objkeyid:
			obj[keyidname] = objkeyid
		return res
	
	def add_object(self, table, obj):
		'''
		Add a object to table
		'''
		keys = ','.join(['%s' % self.__nameliteral__(k) for k in obj.keys()])
		vals = ','.join([self.__literal__(v) for v in obj.values()])
		sql = 'insert into %s(%s) values(%s)' % (self.__nameliteral__(table), keys, vals)
		return self.exe_sql(sql, self.autocommit)	
	
	def create_table(self, table, tplobj, keyidname='id', new=False):
		'''
		Create a table by a template object's property
		'''
		global __dbtype__
		if new:
			# drop table before start to create
			sql = 'drop table if exists %s' % self.__nameliteral__(table)
			self.exe_sql(sql)
		if not tplobj.has_key(keyidname):
			if self.__dbtype__ == __TYPE_SQLITE__:
				tplobj[keyidname] = 'integer not null'  # SQLite
			elif self.__dbtype__ == __TYPE_MYSQL__:
				tplobj[keyidname] = 'int not null auto_increment' # MySQL
			elif self.__dbtype__== __TYPE_PGDB__:
				tplobj[keyidname] = 'bigserial not null' # PostgreSQL
		struct = ','.join(['%s %s' % (self.__nameliteral__(k), self.__typemap__(v)) for (k, v) in tplobj.items()])
		struct = '%s,%s' % (struct, 'primary key (%s)' % self.__nameliteral__(keyidname))
		sql = 'create table%s %s(%s)' % (__ifornot__(self.__dbtype__ == __TYPE_MYSQL__, ' if not exists', ''), self.__nameliteral__(table), struct)
		return self.exe_sql(sql, self.autocommit)
	
	def reset_table(self, table):
		'''
		Clear all record by table name
		'''
		sql = 'truncate table %s' % self.__nameliteral__(table)
		return self.exe_sql(sql, self.autocommit)
	
	def drop_table(self, table):
		'''
		Drop the data and table
		'''
		sql = 'drop table %s' % self.__nameliteral__(table)
		return self.exe_sql(sql, self.autocommit)
	
	
	