from pymongo import MongoClient
from urllib import parse

def mongodb():
    username = parse.quote_plus("openeyes")         #RFC 3986转义
    password = parse.quote_plus("Openeyes@2020")   #RFC 3986转义
    client = MongoClient('mongodb://{0}:{1}@127.0.0.1:27017/'.format(username, password))
    db = client['openeyes']
    return db

def del_openeyes():
    db = mongodb()
    tables = db.collection_names()
    if len(tables) > 0:
        for table in tables:
            db.drop_collection(table)