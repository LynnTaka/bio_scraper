from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(query_vector, faculty_vectors):
    # calc cosine sim btw query and faculty vectors
    similarity_scores = cosine_similarity(query_vector, faculty_vectors)
    return similarity_scores

def get_top_five_most_similar(sim_scores, faculty_pages):
    scored_pages = list(zip(sim_scores[0], faculty_pages))
    ranked_pages = sorted(scored_pages, key=lambda x: x[0], reverse=True)
    top_five = ranked_pages[:5]

    return top_five
