import asyncio
import pymongo
import ssl
from datetime import datetime as dt
default_dt = dt.now()

mongo_client = pymongo.MongoClient("mongodb+srv://wingforse:5oRyqAQD5i7tUzfL@psyhelperbot-df36j.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_ca_certs=/Users/chef/Library/Python/3.7/lib/python/site-packages/certifi/cacert.pem")

# mongo_client.users collection schema
# {
#   name: <String>,
#   surname: <String>,
#   tg_id: <String>,
#   phone: <Integer>
# }

# mongo_client.records
# {
#   time: <DateTime>,
#   user: <ObjectID>,
#   comments: [<MessageID_1>, <MessageID_2>, ... ]     There can be id of messages with audio, text and either a video
# }

db_main = mongo_client.PsyHelperBot

users = db_main.users
records = db_main.records
settings = db_main.settings


# Add a new entry 'user'
async def new_user(name='', surname='', tg_id='', phone=''):
    user_objid = users.insert_one({
                                'name': name,
                                'surname': surname,
                                'tg_id': tg_id,
                                'phone': phone
                                }).inserted_id
    return user_objid

async def get_user(tg_id):
    user = users.find_one({'tg_id': tg_id})
    return user

# If it is a new user after record ask him to fill his name, surname and phone
async def new_record(dt=default_dt, tg_id=''):      # comments will be only in update case
    user = await get_user(tg_id)
    if user is None:
        user_objid = await new_user(tg_id=tg_id)
    else:
        user_objid = user['_id']

    record = records.insert_one({
                                    'time': time,
                                    'user': user_objid
                                    })
    return record

async def get_records_by_user(tg_id):
    user = await get_user(tg_id)
    if user is None:
        user_objid = await new_user(tg_id=tg_id)
    else:
        user_objid = user['_id']
    records_cur = records.find({'user': user_objid})
    return records_cur

def get_settings():
    return settings.find_one({})