from flask_mvc.model.generic import Types, Connection
from flask_mvc.model.generic import ModelObject as ModelObjectG
_have_pg = False
try:
    import psycopg2 as pg
    _have_pg = True
except ImportError:
    pass

if _have_pg:
    
    class PSQLTypes(Types):
        pass


    class PSQLConnection(Connection):
        _db=None
        def __init__(self, connection_string):
            self.conn = pg.connect(connection_string)
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
        
        def rollback(self):
            self.conn.rollback()

        def execute(self, sql, args=()):
            try:
                self.cursor.execute(sql,args)
            except pg.ProgrammingError:
                self.rollback()
                raise
            except pg.DataError as e:
                self.rollback()
                raise pg.DataError(e.message + ' : ' + sql)
        



