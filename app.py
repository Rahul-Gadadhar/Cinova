from flask import Flask, render_template, request
import requests
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from time import time
from val import com_mov
from decouple import config
app = Flask(__name__)

# Load the Word2Vec model and movie embeddings
loaded_model = Word2Vec.load("word2vec_model.bin")
loaded_movie_features_df = pd.read_csv("movie_feature_vectors.csv", index_col=0)
loaded_movie_description_embeddings = {
    movie_title: loaded_movie_features_df.loc[movie_title].values
    for movie_title in loaded_movie_features_df.index
}

def get_embedding(text, word2vec_model):
    words = text.split()
    words = [word.lower() for word in words]
    embeddings = [word2vec_model.wv[word] for word in words if word in word2vec_model.wv]

    if embeddings:
        embedding = np.mean(embeddings, axis=0)
        return embedding
    else:
        return None

def get_recommendations(query_description, embeddings):
    query_embedding = get_embedding(query_description.lower(), loaded_model)
    if query_embedding is not None:
        similarities = {}
        for movie_id, movie_embedding in embeddings.items():
            similarity = cosine_similarity([query_embedding], [movie_embedding])[0][0]
            similarities[movie_id] = similarity
        recommended_movies = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return recommended_movies
    else:
        return []


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    api_key = config('API_KEY')
    num_sug = int(request.form['num_suggestions'])
    query_description = request.form['query_description']
    genre = request.form['genre']
    actor = request.form['actor']
    year = None
    rate = request.form['rate']

    recommended_movies = get_recommendations(query_description, loaded_movie_description_embeddings)
    
    real = com_mov(actor, genre, rate, year, recommended_movies)

    movie_details = []
    for movie_title in real[:num_sug]:
        tmdb_id = int(movie_title)
        base_url = 'https://api.themoviedb.org/3/'
        url = f'{base_url}movie/{tmdb_id}?api_key={api_key}'
        response = requests.get(url)
        credits_url = f'{base_url}movie/{tmdb_id}/credits?api_key={api_key}'
        credits_response = requests.get(credits_url)
        if credits_response.status_code == 200:
            cast_data = credits_response.json()['cast']
            cast =", ".join([actor['name'] for actor in cast_data[:10]])
        if response.status_code == 200:
            movie_data = response.json()
            poster_url = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}"
            movie_data['poster_url'] = poster_url
            movie_data["cast"] = cast
            movie_details.append(movie_data)
        else:
            print(f'Error: {response.status_code}')

    return render_template('index.html', movie_details=movie_details)
if __name__ == '__main__':
    app.run(debug=True)
