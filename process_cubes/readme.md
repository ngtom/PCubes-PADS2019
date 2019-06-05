# Process Cubes Webservice

## Requirements

 - Django
 - Djongo
 - dnspython
 - PM4Py
 - django-tables2
 - (MongoDB)

## Developers FAQ

### Getting started

 - Install the requirements defined in the `requirements.txt`, e.g. by running: `pip install -r requirements.txt`.
 - Install MongoDB
 - run: `python manage.py migrate --run-syncdb` to create the document collections
 - run `python manage.py runserver` to start the webservice

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

How is the data stored in the database?
Have a look at the design specification document. It describes the data model. Additionally, have a look at the `import_xes` function in the `import_xes` module to see how the log is stored in the database.

Currently, the most models are defined in the `models.py` of the `import_xes` app.
Slice and Dice objects should be in the `slice-dice` app.

#### Events
Events are stored in the `events` collection. One document (or object) in this collection stores for each attribute a value. 
Each event has the attribute names as keys and the values as values.
Attributes of traces start with 'trace:'.
The ID of the corresponding trace is stored in `trace:_id`.

Example:
```
{
    "_id":"5ce43529aca227ddfe30a572",
    "org:group":"A",
    "lifecycle:transition":"complete",
    "concept:name":"ER Sepsis Triage",
    "time:timestamp":"2014-12-21T11:15:45.000Z",
    "trace:concept:name":"B",
    "trace:_id":"5ce43528aca227ddfe30a13e",
    "log":8
}
```

#### Traces

Traces are stored in the `traces` collection. Similar to events, each trace object has its attributes as keys and a value as value. 
Each trace stores the ID of its trace. The trace itself doesn't store which events belong to the trace.

Example:
```
{
    "_id":"5ce43528aca227ddfe30a13e",
    "concept:name":"B",
    "log":8
}
```


#### MongoDB

Currently we use a free MongoDB Atlas instance. 
If you want to use your local MongoDB instance change the host in the `DATABASE` variable in  `settings.py`.

The Database can be explored with MongoDB Compass. Use this link `mongodb+srv://pcubes:pcubes2019@cluster0-zxaok.mongodb.net/test?retryWrites=true` to access it.

#### How do I access the database?

For everything that is implemented with Django Models, i.e. exisits as a class in `models.py`:
https://docs.djangoproject.com/en/2.2/ref/models/querysets/

Events and Traces are not modeled as Django models. These are stored directly in the database with PyMongo.

For example to get all events for a given event log:
```
client = MongoClient(host=DATABASES['default']['HOST'])
db = client[DATABASES['default']['NAME']]
event_collection = db['events']

t1 = time.time()
events = event_collection.find({'log': log.id}
```
Tutorial: http://api.mongodb.com/python/current/tutorial.html
