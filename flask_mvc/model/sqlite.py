import sqlite3
import yaml
from flask_mvc.model.generic import Types, Connection
from flask_mvc.model.generic import ModelObject as ModelObjectG

class SQLiteTypes(Types):
    small_string='TEXT'
    string='TEXT'
    integer='INTEGER'
    float='REAL'
    real='REAL'
    numeric='NUMERIC'
    boolean='NUMERIC'
    date='NUMERIC'
    datetime='NUMERIC'
    double='REAL'


class SQLiteConnection(Connection):
    _db=None
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()
    def close(self):
        self.conn.close()
    def commit(self):
        self.conn.commit()
    def commit_and_close(self):
        self.commit()
        self.close()
    def __enter__(self):
        self.cursor = self.conn.cursor()
    def __exit__(self, type, value, traceback):
        self.commit_and_close()
    def execute(self, sql, args=()):
        try:
            self.cursor.execute(sql,args)
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(e.message + ' : ' + sql)



