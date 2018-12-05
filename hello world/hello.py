# импортируем pymongo
import sys

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
def main():
     try:
         client = MongoClient()
         print("Connected")
         db=client["test"]
         print(db.list_collection_names())
         data=db["users"]
         for post in data.find():
             print(post)
     except ConnectionFailure as e:
         sys.stderr.write("could not connect to MongoDB")
         sys.exit(1)

if __name__ =="__main__" :
    main()
