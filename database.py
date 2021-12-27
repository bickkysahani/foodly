import os
import pymongo
client = pymongo.MongoClient("mongodb+srv://recepie:helloworld1!@cluster0.i8ody.mongodb.net/cook_club?retryWrites=true&w=majority")
db = client["cook_club"]
# print(db.list_collection_names())