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

#### 2. Create an Object Type

```python
from flask_mvc.model.sqlite import ObjectFactory
User = ObjectFactory.create_from_yaml('User', 'User.yml')
```

#### 3. Initialize the Object type in the database

```python
# This creates the table 
User.initialize()
```

#### 4. Enter some data

```python
luke = User(id=0, name='Luke', age=26)
luke.create(con)
sean = User(id=1, name='Sean', age=27)
sean.create(con)
```

#### 5. Get some data

```python
print User.list(con)
> [<User id=0,name=Luke,age=26>, <User id=1,name=Sean,age=27>]
```

#### 6. Narrow it down

```python
print User.where(con, 'name="Luke"')
> [<User id=0,name=Luke,age=26>]
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

