from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from sklearn.feature_extraction.text import CountVectorizer
import pymongo

class BioParser:
    def __init__(self):
        pass
    def connectDB(self):
        DB_NAME = 'CPPBIO'
        DB_HOST = 'localhost'
        DB_PORT = 27017
        client = pymongo.MongoClient(DB_HOST, DB_PORT)
        db = client[DB_NAME]
        self.pages = db.pages
        self.faculty = db.faculty

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
    

    def parse_homepage(self, url):
        try:
            html = urlopen(url)
            bs = BeautifulSoup(html, 'html.parser')
            # Initialize dictionary to store extracted information
            faculty_info = {}
            # Extract content from the 'div.fac-info' section
            fac_info = bs.find('div', {'class': 'fac-info'})
            if fac_info:
                faculty_info['fac_info'] = fac_info.get_text(separator='\n').strip()
            # Extract content from the 'div.fac-staff' section
            fac_staff = bs.find('div', {'class': 'fac-staff'})
            if fac_staff:
                faculty_info['fac_staff'] = fac_staff.get_text(separator='\n').strip()
            # Extract content from the 'div.accolades' section
            accolades = bs.find('div', {'class': 'accolades'})
            if accolades:
                faculty_info['accolades'] = accolades.get_text(separator='\n').strip()

            return faculty_info
        except (HTTPError, URLError) as e:
            print("Access failed:", url + " Error Type:", e)
            return None


    def index_faculty_homepages(self):
        # Get all documents from the faculty collection
        faculty_pages = self.faculty.find({}, {'url': 1})
        for page in faculty_pages:
            homepage_url = page['url']
            # Parse the homepage and extract relevant information
            faculty_info = self.parse_homepage(homepage_url)
            if faculty_info:
                try:
                    # Check if any of the sections are missing and skip updating if so
                    if 'fac_info' not in faculty_info or 'fac_staff' not in faculty_info or 'accolades' not in faculty_info:
                        print(f"Skipping indexing for {homepage_url}: Missing sections")
                        continue
                    # Update the faculty document with the extracted information
                    self.faculty.update_one({'url': homepage_url}, {'$set': faculty_info}, upsert=True)
                    print(f"Homepage indexed: {homepage_url}")
                except Exception as e:
                    print(f"Failed to index homepage {homepage_url}. Error: {e}")



    def process_text(self):
        vectorizer = CountVectorizer(stop_words = 'english')
        faculty = self.faculty.find({})

        # iterate through every document within the faculty collection.
        for prof in faculty:
            # acquire all text from the attributes
            text = prof.get('fac_info', '') + ' ' + prof.get('fac_staff', '') + ' ' + prof.get('accolades', '')
            #tokenize the text
            tokenized_text = vectorizer.fit_transform([text])
            #get vocabulary
            vocabulary = vectorizer.vocabulary_
            #get tokens from vocabulary
            tokens = list(vocabulary.keys())
            #save tokens as 'tokens' attribute in the respective document
            self.faculty.update_one({'_id': prof['_id']}, {'$set': {'tokens': tokens}})



