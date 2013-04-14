Flask MVC
=========
A framework to extend [Flask](http://flask.pocoo.org) to follow the model view controller, MVC, web application development pattern.


Usage
=====

SQLite3 Object Relational Map
-----------------------------

#### 1. Define an Object Schema

```yml
User:
  id: integer*
  name: string
  age: integer
```

#### 2. Create the connection

```python
from flask_mvc.model.sqlite import SQLiteConnection
conn = SQLiteConnection(':memory:')
```

#### 3. Initialize the Object Type
```python
from flask_mvc.model.sqlite import SQLiteTypes
User = SQLiteTypes.create_from_yaml('User', 'User.yml')
```

#### 4. Initialize the Object type in the database

```python
# This creates the table 
User.initialize(conn)
```

#### 5. Enter some data

```python
luke = User(id=0, name='Tony Stark', age=26)
luke.create(conn)
sean = User(id=1, name='Rowdy', age=27)
sean.create(conn)
```

#### 6. Get some data

```python
print User.list(conn)
> [<User id=0,name=Tony Stark,age=26>, <User id=1,name=Rowdy,age=27>]
```

#### 7. Narrow it down

```python
print User.where(conn, 'name="Tony Stark"')
> [<User id=0,name=Tony Stark,age=26>]
```

#### 8. Better method to narrow it down

```python
print User.where_name_is(conn, 'Tony Stark',one=True)
> <User id=0,name=Tony Stark,age=26>
```


Author
------
Luke Campbell luke.s.campbell at-symbol gmail.com

Copying
-------

    Copyright 2013 Luke Campbell

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

