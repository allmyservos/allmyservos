#!/usr/bin/python
#######################################################################
# AllMyServos - Fun with PWM
# Copyright (C) 2015  Donate BTC:14rVTppdYQzLrqay5fp2FwP3AXvn3VSZxQ
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#######################################################################
import sqlite3 as lite, sys, inspect, itertools, traceback, os, json

class DB:
	operands = [ '<', '<=', '=', '=>', '>', 'LIKE' ]
	def __init__(self, dbpath = 'app.db'):
		'''
		instances the DB object
		
		used for interfacing with SQLite
		'''
		self.dbpath = dbpath
		basepath = os.path.dirname(dbpath)
		if(len(basepath) > 1 and not os.path.exists(basepath)):
			os.makedirs(basepath)
		try:
			con = self.open()
			cur = con.cursor()
			try:
				self.version = DB.version
			except:
				cur.execute('SELECT SQLITE_VERSION()')
				self.version = DB.version = str(cur.fetchone()[0])
			cur.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name != 'android_metadata' AND name != 'sqlite_sequence'")
			self.tablecount = cur.fetchone()
		except lite.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		finally:
			con.close()
	def open(self):
		'''
		prepares the connection
		'''
		return lite.connect(self.dbpath)
	def createTable(self, name, primary = 'rowid', cols = {}):
		'''
		creates an SQLite table based on the arguments
		'''
		con = self.open()
		cur = con.cursor()
		colstrings = {}
		for key, val in cols.items():
			colstrings[len(colstrings)] = key+' '+val
		cur.execute("CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT, {2})".format(name, primary, ','.join(colstrings.values())))
		con.commit()
		con.close()
	def addRow(self, table, vals):
		'''
		adds a row to the SQLite database
		'''
		con = self.open()
		cur = con.cursor()
		fields = vals.keys()
		results = vals.values()
		cur.execute("INSERT INTO {0} ({1}) VALUES({2})".format(table, ', '.join(f for f in fields), ', '.join('?' for f in fields)),results)
		con.commit()
		con.close()
		return cur.lastrowid
	def addRows(self, table, vals):
		'''
		adds multiple rows in a single query
		'''
		fields = vals.keys()
		results = vals.values()
		con = self.open()
		cur = con.cursor()
		cur.executemany('INSERT INTO ? () VALUES ({0})'.format(table,', '.join('?' for f in fields)),results)
		con.commit()
		con.close()
	def updateRow(self,table, vals, expr = ''):
		'''
		updates a row to the SQLite database
		'''
		fields = vals.keys()
		results = vals.values()
		con = self.open()
		cur = con.cursor()
		cur.execute('UPDATE {0} SET {1} WHERE {2};'.format(table, ', '.join(str(f) + '=?' for f in fields),expr),results)
		con.commit()
		con.close()
	def deleteRow(self, table, expr):
		'''
		deletes a row to the SQLite database
		'''
		con = self.open()
		cur = con.cursor()
		cur.execute("DELETE FROM {0} WHERE {1}".format(table,expr))
		con.commit()
		con.close()
	def getRow(self,table,expr = '', collist = {}):
		'''
		retrieves a row to the SQLite database
		'''
		con = self.open()
		cur = con.cursor()
		if(len(collist) > 0):
			sql = "SELECT {0} FROM {1} WHERE {2}".format(','.join(collist),table,expr)
		else:
			sql = "SELECT * FROM {0} WHERE {1}".format(table,expr)
		cur.execute(sql)
		res = cur.fetchone()
		con.close()
		return res
	def getRows(self,table,expr = '', order = ''):
		'''
		retrieves multiple rows from the SQLite database
		'''
		rows = {}
		con = self.open()
		cur = con.cursor()
		sql = 'SELECT * FROM {0}'.format(table)
		if(isinstance(expr, (list, tuple))):
			if(any(expr)):
				sql += " WHERE "
				if(len(expr) == 3 and expr[1] in DB.operands):
					if(isinstance(expr[2], (int, long, float, complex))):
						sql += '"{0}" {1} {2}'.format(expr[0],expr[1],expr[2])
					elif(isinstance(expr[2], (str, unicode))):
						sql += '"{0}" {1} \'{2}\''.format(expr[0],expr[1],expr[2])
				else:
					parts = []
					for x in expr:
						if(isinstance(x, (list, tuple))):
							if(len(x) == 3):
								if(isinstance(x[2], (int, long, float, complex))):
									parts.append('"{0}" {1} {2}'.format(x[0],x[1],x[2]))
								elif(isinstance(x[2], (str, unicode))):
									parts.append('"{0}" {1} \'{2}\''.format(x[0],x[1],x[2]))
						elif(isinstance(x, (str, unicode))):
							if(len(x) > 0):
								parts.append(x)
					sql += " AND ".join(parts)
		elif(len(expr) > 0):
			sql += " WHERE {0}".format(expr)
		if(len(order) > 0):
			sql += " ORDER BY {0}".format(order) 
		cur.execute(sql)
		res = cur.fetchall()
		con.close()
		return res
class Table(object):
	def __init__(self, dbpath = 'app.db', tname = None, primary = 'rowid', cols = {}):
		'''
		a generic object used to map object attributes directly to SQLite columns
		'''
		try:
			Table.checks
		except:
			Table.checks = []
			Table.modules = {}
			Table.colLists = {}
			Table.constructors = {}
		self.db = DB(dbpath)
		if(tname != None):
			self.__sql_name = tname
		else:
			self.__sql_name = type(self).__name__
		try:
			self.__sql_primary
		except:
			self.__sql_primary = primary
		try:
			self.__sql_cols
		except:
			if(len(cols) > 0):
				self.__sql_cols = cols
			else:
				self.parseAttributes()
		self.check()
	def parseAttributes(self, omit = []):
		'''
		nominates attributes based on their data type
		'''
		try:
			Table.colLists[self.__sql_name]
		except:
			self.__sql_cols = {}
			attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
			for a in attributes:
				if not(a[0].startswith('__') and a[0].endswith('__')) and not(a[0].startswith('_')) and not(a[0] in omit):
					if(isinstance(a[1], (int, long, float, complex))):
						self.__sql_cols[a[0]] = 'real'
					elif (isinstance(a[1], (str, unicode))):
						self.__sql_cols[a[0]] = 'text'
			Table.colLists[self.__sql_name] = self.__sql_cols
		else:
			self.__sql_cols = Table.colLists[self.__sql_name]
	def check(self):
		'''
		confirms the table corresponding to this object is present. if not, create it.
		'''
		if(not self.__sql_name in Table.checks):
			self.db.createTable(self.__sql_name, self.__sql_primary, self.__sql_cols)
			Table.checks.append(self.__sql_name)
			Table.modules[self.__sql_name] = __import__(type(self).__module__)
			Table.constructors[self.__sql_name] = getattr(Table.modules[self.__sql_name],self.__sql_name)
	def query(self, expr = '', order = '', keyindex = False):
		'''
		run a select query on this table and return the results in the form of instances of this object
		'''
		rows = self.db.getRows(self.__sql_name, expr, order)
		instances = {}
		if(len(rows) > 0):
			collist = self.getColList()
			if(not keyindex):
				nind = 0
			for r in rows:
				if(keyindex):
					ind = r[0]
				else:
					ind = nind
					nind += 1
				instances[ind] = self.__unpack(collist, r)
			return instances
		return {}
	def __unpack(self, collist, row, newinstance = True):
		'''
		convenience function which mirrors row values onto an object
		'''
		args = {}
		primary = {}
		for k, v in enumerate(row):
			if(collist[k] != self.__sql_primary):
				args[collist[k]] = row[k]
			else:
				primary = { collist[k] : row[k] }
		instance = Table.constructors[self.__sql_name](**args)
		if(len(primary) == 1):
			setattr(instance,primary.keys()[0],primary.values()[0])
		return instance
	def getSqlName(self):
		return self.__sql_name
	def getPrimaryKey(self):
		return self.__sql_primary
	def getColList(self, addprimary = True):
		'''
		returns a list containing the current columns
		'''
		if(addprimary):
			return [ self.__sql_primary ] + self.__sql_cols.keys()
		else:
			return self.__sql_cols.keys()
	def save(self):
		'''
		commits the values of the current attributes to the SQLite database
		'''
		fields = self.__sql_cols.keys()
		valset = {}
		for f in fields:
			valset[f] = getattr(self,f)
		if(hasattr(self,self.__sql_primary) and isinstance(getattr(self, self.__sql_primary), int)):
			self.db.updateRow(self.__sql_name,valset,self.__sql_primary+'={0}'.format(getattr(self,self.__sql_primary)))
		else:
			id = self.db.addRow(self.__sql_name,valset)
			setattr(self,self.__sql_primary, id)
	def load(self, index):
		'''
		loads the values from the SQLite database into corresponding attributes
		'''
		if(isinstance(index, (int, long, float, complex))):
			collist = self.getColList()
			row = self.db.getRow(self.__sql_name,self.__sql_primary+'={0}'.format(int(index)), collist)
			if(row != None):
				for k, v in enumerate(row):
					setattr(self,collist[k],row[k])
				return self
		return None
	def reload(self):
		self.load(getattr(self,self.__sql_primary));
	def loadBy(self,wheres = {}):
		'''
		like load but an expression can be provided
		'''
		wset = {}
		fields = wheres.keys()
		values = wheres.values()
		ind = 0
		collist = self.getColList()
		for f in fields:
			if(isinstance(values[ind], bool)):
				wset[ind] = '"{0}"={1}'.format(fields[ind], 1 if values[ind] else 0)
			elif(isinstance(values[ind], (int, long, float, complex))):
				wset[ind] = '"{0}"={1}'.format(fields[ind],values[ind])
			else:
				wset[ind] = '"{0}"=\'{1}\''.format(fields[ind],values[ind])
			ind+=1
		row = None
		try:
			row = self.db.getRow(self.__sql_name,' AND '.join(wset.values()),collist)
		except Exception, e:
			print(e)
			print(wset)
		if(row != None):
			return self.__unpack(collist, row)
		return None
	def delete(self):
		'''
		removes a row from the SQLite database
		'''
		self.db.deleteRow(self.__sql_name, self.__sql_primary+'={0}'.format(getattr(self,self.__sql_primary)))