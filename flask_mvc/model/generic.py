import yaml
from flask_mvc.utils.yaml_loader import OrderedDictYAMLLoader
from flask_mvc.utils.pluralize import pluralize


class Types(object):
    attrs=['small_string','string','integer','float','real','numeric','boolean','date','datetime','double','memo']
    
    small_string='VARCHAR(32)'
    string='VARCHAR(128)'
    integer='INTEGER'
    float='REAL'
    real='REAL'
    numeric='NUMERIC'
    boolean='BOOLEAN'
    date='DATE'
    datetime='TIMESTAMP'
    double='DOUBLE PRECISION'
    memo='TEXT'

    @classmethod
    def not_null(cls, val):
        return '%s NOT NULL' % val
    @classmethod
    def primary_key(cls, val):
        return '%s PRIMARY KEY' % val

    @classmethod
    def primary_keys(cls, vals=[]):
        return 'PRIMARY KEY (%s)' % ','.join(vals)

    @classmethod
    def create(cls, name, table_schema):
        fields = table_schema.keys()
        if 'PRIMARY KEY' in table_schema:
            fields.remove('PRIMARY KEY')
        retval = type(name, (ModelObject,), dict(_table=pluralize(name), _schema=table_schema, _fields=fields, **table_schema))
        for field in table_schema.keys():
            setattr(retval,'where_%s_is' % field, classmethod(WhereIsWrapper(field)))
        return retval

    @classmethod
    def create_from_yaml(cls, name, filepath):
        schema = cls.parse_model(filepath)
        return cls.create(name,schema[name])
    
    @classmethod
    def _parse_fields(cls, fields):
        primary_keys = [k for k,v in fields.iteritems() if v.endswith('*')]
        primary_key_count = len(primary_keys)
        if not primary_key_count:
            raise ValueError('No primary key defined')
        for field, value in fields.iteritems():
            modifier = lambda x:x
            if value.endswith('*'):
                if primary_key_count==1:
                    modifier = cls.primary_key
                value = value[:-1]
            elif value.endswith('+'):
                modifier = cls.not_null
                value = value[:-1]
            if value in cls.attrs:
                fields[field] = modifier(getattr(cls,value))
            else:
                raise TypeError('Unknown schema field type: %s' % value)
        if primary_key_count > 1:
            fields['PRIMARY KEY'] = cls.primary_keys(primary_keys)

    @classmethod
    def parse_model(cls, definition):
        schema = {}
        with open(definition,'r') as f:
            schema = yaml.load(f.read(), Loader=OrderedDictYAMLLoader)
        for table,fields in schema.iteritems():
            cls._parse_fields(fields)
        return schema

class Connection(object):
    _db=None
    def __init__(self, connection_string):
        raise NotImplementedError('Abstract Class')
    
    def close(self):
        raise NotImplementedError('Abstract Class')
    
    def commit(self):
        raise NotImplementedError('Abstract Class')
    
    def commit_and_close(self):
        raise NotImplementedError('Abstract Class')
    
    def __enter__(self):
        raise NotImplementedError('Abstract Class')
    
    def __exit__(self, type, value, traceback):
        raise NotImplementedError('Abstract Class')

    def query_db(self,query, args=(), one=False):
        self.execute(query,args)
        retval = [{self.cursor.description[idx][0]:value for idx,value in enumerate(row)} for row in self.cursor.fetchall()]
        return (retval[0] if retval else None) if one else retval

    def create_tables(self, schema):
        commands = []
        for table,fields in schema.iteritems():
            sql = self.create_table(table,fields)
            commands.append(sql)
        return commands
    
    def create_table(self, name, table_schema):
        sql = 'CREATE TABLE %s(' % name
        sql += ','.join(['%s %s' % (field,value) for field,value in table_schema.iteritems() if field != 'PRIMARY KEY'])
        if 'PRIMARY KEY' in table_schema:
            sql += ', %s' % table_schema['PRIMARY KEY']
        sql += ')'
        self.execute(sql)
        self.commit()
        return sql

    def drop_table(self, name):
        sql = 'DROP TABLE IF EXISTS %s' % name
        self.execute(sql)
        self.commit()
        return sql

    def insert(self, table, values=[]):
        sql = 'INSERT INTO %s VALUES(' % table
        for i,value in enumerate(values):
            if value is None:
                values[i] = 'NULL'
            if isinstance(value,basestring):
                value = value.replace("'",'"')
                values[i] = "'%s'" % value
        sql += ','.join([str(v) for v in values])
        sql += ')'
        self.execute(sql)
        self.commit()
        return sql

    def execute(self, sql, args=()):
        raise NotImplementedError('Abstract Class')

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
            elif key == 'PRIMARY KEY':
                continue
            else:
                raise AttributeError('%s not defined in object schema.' % key)
    def __repr__(self):
        retval = '<%s ' % self.__class__.__name__
        retval += ','.join(['%s=%s' %(k,getattr(self,k)) for k in self._fields])
        retval +='>'
        return retval

    def iteritems(self):
        for field in self._fields:
            try:
                v = getattr(self,field)
            except AttributeError:
                v = None
            yield field, v
        return

    def csv(self):
        return ','.join([getattr(self,f) for f in self._fields])

    @classmethod
    def initialize(cls, connection):
        connection.create_table(cls._table, cls._schema)

    @classmethod
    def reinitialize(cls, connection):
        connection.drop_table(cls._table)
        cls.initialize(connection)

    def create(self, connection):
        connection.insert(self._table,[getattr(self,f) for f in self._fields])

    @classmethod
    def where(cls, connection, expr, one=False):
        query = 'SELECT * FROM %s WHERE %s' % (cls._table,expr)
        retval = connection.query_db(query,one=one)
        return [cls(**i) for i in retval] if not one else cls(**retval)

    @classmethod
    def list(cls, connection, limit=None):
        query = 'SELECT * FROM %s' % cls._table
        if limit:
            query += ' LIMIT ?'
            return [cls(**i) for i in connection.query_db(query,[limit])]
        return [cls(**i) for i in connection.query_db(query)]

    def __eq__(self, other):
        return vars(self) == vars(other)

    def pretty_format(self):
        return '\n'.join(['%s: %s' %(k,v) for k,v in self.iteritems()])
        


class FieldWrapper(object):
    def eval(self, value):
        if isinstance(value, basestring):
            return "'%s'" % value
        elif isinstance(value, (int,float)):
            return value
        


class WhereIsWrapper(FieldWrapper):
    def __init__(self,field):
        self.field = field
    def __call__(self, cls, connection, val, one=False):
        query = 'SELECT * FROM %s WHERE %s=%s' % (cls._table,self.field, self.eval(val))
        return cls(**connection.query_db(query,one=one)) if one else [cls(**i) for i in connection.query_db(query,one=one)]

