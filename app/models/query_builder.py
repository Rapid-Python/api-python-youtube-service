import pymongo
from datetime import datetime
from bson.objectid import ObjectId

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


def fetch_course(course_name=None):
    db = client['course']
    info = db[course_name]
    return list(info.find({}, {'_id': 0}))


def check_access(id, access):
    db = client['user']
    info = db['user_info']
    return info.find_one({'user_id': id, 'access_type': access})


def insert_video(course_id, data):
    db = client['courses']
    info = db['course_detail']
    data['course_id'] = course_id
    data['createAt'] = datetime.now()
    info.insert_one(data)


def access_type(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one({'user_id': user_id}, {'_id': 0, 'access_type': 1})


def fetch_courses():
    db = client['courses']
    info = db['course']
    return list(info.find({}))


def fetch_users():
    db = client['user']
    info = db['user_info']
    return list(info.find({}))


def insert_course(course_detail):
    db = client['courses']
    info = db['course']
    course_id = str(info.insert_one(course_detail).inserted_id)
    return course_id


def update_course(object_id, course_detail):
    db = client['courses']
    info = db['course']
    info.update_one(
        {
            '_id': ObjectId(object_id)
        },
        {
            "$set": course_detail
        }
    )


def delete_course(object_id):
    db = client['courses']
    info = db['course']
    info.delete_one({'_id': ObjectId(object_id)})


def course_video(course_id):
    db = client['courses']
    info = db['course_detail']
    return list(info.find({'course_id': course_id}))
