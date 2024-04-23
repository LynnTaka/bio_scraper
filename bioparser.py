from bs4 import BeautifulSoup
import pymongo

class BioParser:
    def __init__(self):
        pass
    def connectDB(self):
        """
        connect database
        :return: none
        """
        # database info
        DB_NAME = 'CPPBIO'
        DB_HOST = 'localhost'
        DB_PORT = 27017

        # connect to db
        client = pymongo.MongoClient(DB_HOST, DB_PORT)
        self.db = client[DB_NAME]
        self.pages = self.db.pages

    def query_database(self):
        """
        query database to get data from database
        :return: dictionary of info from html pages to parse through later
        """
        # regex for url
        re = "^https://www.cpp.edu/faculty/"

        # execute query
        result = self.pages.find({"url": {"$regex": re}})

        # check results
        # for i, document in enumerate(result):
        #     print(f'{i} {document}')

        return result



