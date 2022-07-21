import pymongo
from datetime import datetime

url = "mongodb://localhost:27017"

client = pymongo.MongoClient(url)


def user_exists(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one({'user_id': user_id})


def insert_user(data):
    if not user_exists(data['user_id']):
        db = client['user']
        info = db['user_info']
        data['createAt'] = datetime.now()
        data['access_type'] = ['user']
        info.update_one(
            {"user_id": data['user_id']},
            {"$set": data},
            upsert=True
        )


def fetch_courses():
    db = client['course']
    return db.list_collections()


def fetch_course(course_name=None):
    db = client['course']
    info = db[course_name]
    return list(info.find({},{'_id': 0}))


def check_access(id, access):
    db = client['user']
    info = db['user_info']
    return info.find_one({'user_id': id, 'access_type': access})


def insert_video(course_name, data):
    db = client['course']
    info = db[course_name]
    data['createAt'] = datetime.now()
    info.insert_one(data)



