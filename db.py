import sqlite3
import os
from os import path

class DBreg:
    def __init__(self,root_path):
        self.BASE=path.join(root_path,"base/reg.db")
        self.TABLE_WEIGHTS="weights"
        self.TABLE_POST="post"

        if not path.isdir(path.dirname(self.BASE)):
            os.mkdir(path.dirname(self.BASE))
        self.conn=sqlite3.connect(self.BASE)
        with self.conn:
            self.conn.execute("create table if not exists %s (id integer primary key autoincrement, dt varchar(20), weight integer)" % self.TABLE_WEIGHTS)
            self.conn.execute("create table if not exists %s (lastpost varchar(10))" % self.TABLE_POST)

    def reg(self, weight,dt=None):
        try:
            if dt is None:
                sql="insert into %s(dt,weight) values(datetime('now','localtime'),%d)" % (self.TABLE_WEIGHTS, int(weight))
            else:
                sql="insert into %s(dt,weight) values('%s',%d)" % (self.TABLE_WEIGHTS, dt, int(weight))
            with self.conn:
                self.conn.execute(sql)
            return True
        except:
            return False

    def select(self,dt1,dt2):
        try:
            with self.conn:
                return self.conn.execute("select * from %s where datetime(dt) between datetime('%s') and datetime('%s') order by dt" % (self.TABLE_WEIGHTS, dt1, dt2)).fetchall()
        except:
            return []

    def del_weight(self,idw):
        try:
            with self.conn:
                self.conn.execute("delete from %s where id=%d" % (self.TABLE_POST, int(idw)))
                return True
        except:
            return False

    def get_lastpost(self):
        try:
            with self.conn:
                return str(self.conn.execute("select lastpost from %s" % (self.TABLE_POST)).fetchone()[0])
        except:
            return None

    def set_lastpost(self,dt):
        try:
            if self.get_lastpost() is None:
                sql="insert into %s (lastpost) values('%s')" % (self.TABLE_POST,dt)
            else:
                sql="update %s set lastpost='%s'" % (self.TABLE_POST,dt)
            with self.conn:
                self.conn.execute(sql)
            return True
        except:
            return False


