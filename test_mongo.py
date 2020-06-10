import pymongo

db_client = pymongo.MongoClient("mongodb+srv://wingforse:5oRyqAQD5i7tUzfL@psyhelperbot-df36j.mongodb.net/test?retryWrites=true&w=majority")
db = db_client.test
db_admin = db_client.admin

print(db)
print('****************************************')
print(db_admin)