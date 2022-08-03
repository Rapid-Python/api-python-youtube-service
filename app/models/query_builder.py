import os
import re
import pymongo
from datetime import datetime
from bson.objectid import ObjectId

url = os.getenv('mongodb_endpoint')

client = pymongo.MongoClient(url)


def user_active(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one(
        {
            'user_id': user_id,
            'active': True
        }
    )


def fetch_active_courses(sort=-1, field='_id'):
    db = client['courses']
    info = db['course']
    return list(info.find({'active': True}).sort(field, sort))


def fetch_user(user_id):
    db = client['user']
    info = db['user_info']
    return info.find_one(
        {
            'user_id': user_id,
            'active': True
        }
    )


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


def fetch_courses(sort=1, filter='title'):
    db = client['courses']
    info = db['course']
    return list(info.find({}).sort(filter, sort))


def insert_course(course_detail):
    db = client['courses']
    info = db['course']
    #course_detail['active'] = False
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


def fetch_course(course_id=None):
    db = client['courses']
    info = db['course']
    return info.find_one({'_id': ObjectId(course_id)})


def delete_course(object_id):
    db = client['courses']
    info = db['course']
    info.delete_one({'_id': ObjectId(object_id)})


def check_access(user_id, access):
    db = client['user']
    info = db['user_info']
    return info.find_one({'user_id': user_id, 'access_type': access})


def course_video_user(course_id):
    db = client['courses']
    info = db['course_detail']
    return list(info.find({'course_id': course_id, 'active': True}))


def course_video(course_id):
    db = client['courses']
    info = db['course_detail']
    return list(info.find({'course_id': course_id}))


def video_info(video_id):
    db = client['courses']
    info = db['course_detail']
    return info.find_one({'_id': ObjectId(video_id)})


def fetch_course_by_category(category):
    db = client['courses']
    info = db['course']
    return list(info.find({'category': category, 'active': True}))


def fetch_course_by_title(keyword):
    rgx = re.compile(f'.*{keyword}.*', re.IGNORECASE)
    db = client['courses']
    info = db['course']
    return list(info.find({'title': rgx, 'active': True}))
##############################











def insert_video(course_id, data):
    db = client['courses']
    info = db['course_detail']
    data['course_id'] = course_id
    data['createAt'] = datetime.now()
    info.insert_one(data)


def fetch_users():
    db = client['user']
    info = db['user_info']
    return list(info.find({}))









