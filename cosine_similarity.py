from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.stem import PorterStemmer
import pymongo

def calculate_similarity(query_vector, faculty_vectors):
    # calc cosine sim btw query and faculty vectors
    similarity_scores = cosine_similarity(query_vector, faculty_vectors)
    return similarity_scores

def get_top_five_most_similar(sim_scores, faculty_pages):
    # put together scores and the corresponding faculty pages
    scored_pages = list(zip(sim_scores[0], faculty_pages))
    # sort in descending order
    ranked_pages = sorted(scored_pages, key=lambda x: x[0], reverse=True)
    # get top 5 most similar
    top_five = ranked_pages[:5]

    return top_five

def load():
    DB_NAME = 'CPPBIO'
    DB_HOST = 'localhost'
    DB_PORT = 27017
    client = pymongo.MongoClient(DB_HOST, DB_PORT)
    db = client[DB_NAME]
    doc = db.inverted_index.find_one()
    inverted_index = doc.get('index', {})
    
    return inverted_index


def search(input, inverted_index):
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


    query_tfidf = pipeline.fit_transform([input])
    vocabulary = pipeline.named_steps['count'].get_feature_names_out()
    query_matrix = query_tfidf.toarray()

    tfidf_table = {}
    size = len(vocabulary)


    for pos, term in enumerate(vocabulary):
        refs = inverted_index.get(term)
        if refs is None:
            print(f"No result")
            return None
        for ref in refs:
            if ref['weight'] != 0:
                url = ref['url']
                tfidf = ref['weight']

                data = tfidf_table.get(url, [0]*size)
                data[pos] = tfidf

                tfidf_table[url] = data

    tfidf_matrix = []
    profs = []
    for prof, tfidf in tfidf_table.items():
        tfidf_matrix.append(tfidf)
        profs.append(prof)

    score = calculate_similarity(query_matrix, tfidf_matrix)
    top_five = get_top_five_most_similar(score, profs)
    for i in top_five:
        print(i[1])
    pass


index = load()
query = "summer research"
search(query, index)
