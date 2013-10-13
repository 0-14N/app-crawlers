#!/usr/bin/python
#################################################
# author:	chenxiong
# date:		2013-3-28
# 
# python run.py apkdir dbname
# 
# warn: the apkdir and dbname should be abstract
#       path
# apkdir -- the dir contains the apks
# dbname -- the db records which apk is unziped
################################################
import sys
from genSimRP import genSimRP
from os import path, listdir
from os.path import isfile, join
import os
import sqlite3

simple_reports_root = '/home/dao/autoApk/apkCome/NewTrdMrks/simple-reports/'
unziped_apks_root = '/home/dao/autoApk/apkCome/NewTrdMrks/unziped-apks/'

def createTable(dbname):
		global conn
		conn = sqlite3.connect(dbname)
		conn.execute(""" create table unzipedapps(\
						id integer primary key autoincrement,\
						apkpath varchar(256) not null unique,\
						unziped int default 0)""")
		conn.commit()

def updateDB(apkDir):
		global conn
		apks = [ f for f in listdir(apkDir) if isfile(join(apkDir, f))]
		for apk in apks:
				apkPath = join(apkDir, apk)
				try:
						conn.execute("""insert into unzipedapps(apkpath) values(?)""", (apkPath,))
						conn.commit()
						print apkPath
				except sqlite3.IntegrityError:
						continue

def getUnzipedApks():
		unzipedApks = []
		global conn
		c = conn.cursor()
		c.execute("""select * from unzipedapps where unziped = 0""")
		rec = c.fetchall()
		for r in rec:
				unzipedApks.append(r[1])
		c.close()
		return unzipedApks

	

if __name__ == '__main__':
		global conn

		if len(sys.argv) < 3:
				print 'python run.py apkdir dbname'
		else:
				apkDir = path.abspath(sys.argv[1])
				dbname = path.abspath(sys.argv[2])

				#first get the market name and create relate dirs
				#if not exist
				market = apkDir.split('/')[-1]
				reportsOutDir = join(simple_reports_root, market)
				unzipedOutDir = join(unziped_apks_root, market)
				if not path.exists(reportsOutDir):
						os.makedirs(reportsOutDir)
				if not path.exists(unzipedOutDir):
						os.makedirs(unzipedOutDir)

				if path.exists(dbname):
						conn = sqlite3.connect(dbname)
				else:
						createTable(dbname)

				updateDB(apkDir)
				unzipedApks = getUnzipedApks()
				for apk in unzipedApks:
						try:
							genSimRP.main(apk, market, unzipedOutDir, reportsOutDir)
							conn.execute("""update unzipedapps set unziped = 1 where apkPath = ?""", (apk,))
							conn.commit()
						except:
							conn.execute("""update unzipedapps set unziped = -1 where apkPath =?""", (apk,))
							conn.commit()
							continue

				conn.close()
