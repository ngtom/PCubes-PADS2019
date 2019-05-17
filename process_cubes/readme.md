# Process Cubes Webservice

## Requirements

 - Django
 - Djongo
 - dnspython
 - PM4Py
 - django-tables2
 - (MongoDB)

## Developers FAQ

### Django
Getting started: 
https://docs.djangoproject.com/en/2.2/intro/tutorial01/

### Django Apps

Every page/functionality should be in its own Django App. You can create an app with
```python 
python manage.py startapp 
```

After this, the app has to be added to the `INSTALLED_APPS` in the `settings.py` in the "process cubes" app.

### Data

Have a look at the design specification document. It describes the data model. Additionally, have a look at the `import_xes` function in the `import_xes` module to see how the log is stored in the database.

Currently, the most models are in the `models.py` of the `import_xes` app.
Slice and Dice objects should be in the `slice-dice` app.

#### MongoDB

Currently we use a free MongoDB Atlas instance. 
If you want to use your local MongoDB instance change the host in the `DATABASE` variable in  `settings.py`.

The Database can be explored with MongoDB Compass. Use this link `mongodb+srv://pcubes:pcubes2019@cluster0-zxaok.mongodb.net/test?retryWrites=true` to access it.

#### How do I acess the database?

For everything that is implemented with Django Models, i.e. exisits as a class in `models.py`:
https://docs.djangoproject.com/en/2.2/ref/models/querysets/

Events and Traces are not modeled as Django models. These are stored directly in the database with PyMongo.

For exmaple to get all events for a given event log:
```
client = MongoClient(host=DATABASES['default']['HOST'])
db = client[DATABASES['default']['NAME']]
event_collection = db['events']

t1 = time.time()
events = event_collection.find({'log': log.id}
```
Tutorial: http://api.mongodb.com/python/current/tutorial.html