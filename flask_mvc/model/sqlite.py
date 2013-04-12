import sqlite3
import yaml
from flask_mvc.utils.yaml_loader import OrderedDictYAMLLoader


class Types(object):
    attrs=['small_string','string','integer','float','real','numeric','boolean','date','datetime']
    
    small_string='TEXT'
    string='TEXT'
    integer='INTEGER'
    float='REAL'
    real='REAL'
    numeric='NUMERIC'
    boolean='NUMERIC'
    date='NUMERIC'
    datetime='NUMERIC'

    @classmethod
    def not_null(cls, val):
        return '%s NOT NULL' % val
    @classmethod
    def primary_key(cls, val):
        return '%s PRIMARY KEY' % val

def parse_model(definition):
    schema = {}
    with open(definition,'r') as f:
        schema = yaml.load(f.read(), Loader=OrderedDictYAMLLoader)
    for table,fields in schema.iteritems():
        for field, value in fields.iteritems():
            modifier = lambda x:x
            if value.endswith('*'):
                modifier = Types.primary_key
                value = value[:-1]
            elif value.endswith('+'):
                modifier = Types.not_null
                value = value[:-1]
            if value in Types.attrs:
                fields[field] = modifier(getattr(Types,value))
            else:
                raise TypeError('Unknown schema field type: %s' % value)
    return schema

class Connection(object):
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

    def query_db(self,query, args=(), one=False):
        self.cursor.execute(query,args)
        retval = [{self.cursor.description[idx][0]:value for idx,value in enumerate(row)} for row in self.cursor.fetchall()]
        return (retval[0] if rv else None) if one else retval

    def create_tables(self, table_schema):
        commands = []
        for table,fields in schema.iteritems():
            sql = self.create_table(table,fields)
            commands.append(sql)
        return commands
    
    def create_table(self, name, schema):
        sql = 'CREATE TABLE %s(' % name
        sql += ','.join(['%s %s' % (field,value) for field,value in schema.iteritems()])
        sql += ')'
        self.cursor.execute(sql)
        self.commit()
        return sql

    def insert(self, table, values=[]):
        sql = 'INSERT INTO %s VALUES(' % table
        for i,value in enumerate(values):
            if isinstance(value,basestring):
                values[i] = '"%s"' % value
        sql += ','.join([str(v) for v in values])
        sql += ')'
        print sql
        self.cursor.execute(sql)
        self.commit()
        return sql


class ObjectFactory(object):
    @classmethod
    def create(cls, name, table_schema):
        retval = type(name, (ModelObject,), dict(_table=name, _schema=table_schema, _fields=table_schema.keys(), **table_schema))
        return retval



class ModelObject(object):
    _fields = []
    _schema = {}
    _table  = ''
    def __init__(self, *args, **kwargs):
        if len(args) <= len(self._fields):
            for i,arg in enumerate(args):
                setattr(self,self._fields[i],arg)
        for key,value in kwargs.iteritems():
            if key in self._fields:
                setattr(self,key,value)
            else:
                raise AttributeError('%s not defined in object schema.' % key)
    def __repr__(self):
        retval = '<%s ' % self.__class__.__name__
        retval += ','.join(['%s=%s' %(k,getattr(self,k)) for k in self._fields])
        retval +='>'
        return retval

    
    def create(self,connection):
        if not isinstance(connection,Connection):
            raise TypeError('Connection required')

        connection.insert(self._table,[getattr(self,f) for f in self._fields])

    @classmethod
    def where(cls, connection, expr):
        query = 'SELECT * FROM %s WHERE %s' % (cls._table,expr)
        return [cls(**i) for i in connection.query_db(query)]

    @classmethod
    def list(cls, connection):
        query = 'SELECT * FROM %s' % cls._table
        return [cls(**i) for i in connection.query_db(query)]


            

