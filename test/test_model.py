from flask_mvc.model.sqlite import SQLiteTypes, SQLiteConnection
from flask_mvc.model.generic import Connection, Types

import unittest
import pkg_resources

class MockConnection(Connection):
    _db=None
    def __init__(self):
        return
    
    def close(self):
        return
    
    def commit(self):
        return 
    
    def commit_and_close(self):
        return 

    def execute(self, sql, args=()):
        return self.response


class BaseModelTest(unittest.TestCase):
    def setUp(self):
        self.connection = MockConnection()
        self.schema = Types.parse_model(pkg_resources.resource_filename(__name__, 'User.yml'))

    def test_object_factory(self):
        User = Types.create('User', self.schema['User'])
        luke = User(0,'luke',26)
        self.assertEquals(luke._fields, ['id','name','age'])
        self.assertEquals(luke.name,'luke')
        self.assertEquals(luke.id,0)
        self.assertEquals(luke.age,26)



class SQLiteTest(unittest.TestCase):
    
    def setUp(self):
        self.connection = SQLiteConnection(':memory:')
        self.schema = SQLiteTypes.parse_model(pkg_resources.resource_filename(__name__, 'User.yml'))

    def create_table_and_class(self,name):
        obj = SQLiteTypes.create(name, self.schema[name])
        obj.initialize(self.connection)
        return obj

    def test_from_yaml(self):
        User = SQLiteTypes.create_from_yaml('User', pkg_resources.resource_filename(__name__,'User.yml'))
        User.initialize(self.connection)
        gibbs = User(0,'Gibbs',45)
        gibbs.create(self.connection)

        self.assertEquals(User.where(self.connection,'id=0'), [gibbs])

        User.reinitialize(self.connection)

        self.assertEquals(User.where(self.connection,'id=0'), [])


    def test_orm(self):
        User = self.create_table_and_class('User')
        luke = User(0,'luke',26)
        luke.create(self.connection)

        qlist = User.list(self.connection)[0]
        self.assertEquals(luke.name,qlist.name)
        self.assertEquals(luke.id,qlist.id)
        self.assertEquals(luke.age,qlist.age)
        
    def test_where(self):
        User = self.create_table_and_class('User')
        users = [
            User(0,'luke',26),
            User(1,'sean',27),
            User(2,'hippy',22),
            User(3,'tony',32)
            ]
        for u in users:
            u.create(self.connection)

        for user in User.where(self.connection,'age >26'):
            self.assertTrue(user.name in ('tony','sean'))

        self.assertEquals(User.where_name_is(self.connection,'tony',one=True),users[3])

        self.assertEquals(User.list(self.connection, limit=2), users[:2])



@unittest.skip('Not implemented')
class PSQLTest(unittest.TestCase):
    pass
