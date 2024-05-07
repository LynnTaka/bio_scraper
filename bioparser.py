from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from nltk.stem import PorterStemmer
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
        self.inverted_index = db.inverted_index

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
        # Define a stemmer function
        stemmer = PorterStemmer()
        def stem_tokens(tokens):
            return [stemmer.stem(token) for token in tokens]

        #tokenize the text using the stemmer function
        def custom_tokenizer(text):
            vectorizer = CountVectorizer(stop_words='english')
            tokenized_text = vectorizer.build_tokenizer()(text)
            return stem_tokens(tokenized_text)

        # Create a pipeline for tokenization and tf-idf transformation
        pipeline = Pipeline([
            ('count', CountVectorizer(tokenizer=custom_tokenizer)),
            ('tfidf', TfidfTransformer())
        ])

        # iterate through every document within the faculty collection.
        faculty_text = [f.get('fac_info', '') + ' ' + f.get('fac_staff', '') + ' ' + f.get('accolades', '') 
                        for f in self.faculty.find()]

        # Fit the pipeline to the text data
        tfidf_matrix = pipeline.fit_transform(faculty_text)

        #get vocabulary (terms) and their corresponding tf-idf weights
        vocabulary = pipeline.named_steps['count'].get_feature_names_out()
        tfidf_weights = tfidf_matrix.toarray()

        # Create the inverted index
        inverted_index = {}
        for term, weights in zip(vocabulary, tfidf_weights.T):
            inverted_index[term] = [{'url': page['url'], 'weight': weight} 
                                    for page, weight in zip(self.faculty.find({}, {'url': 1}), weights)]

        # Insert the inverted index into the database collection
        self.inverted_index.insert_one({'index': inverted_index})