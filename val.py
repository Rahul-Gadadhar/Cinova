import requests
import pandas as pd

def com_mov(a, g, min_rating, year, doc):
    api = 'cef81653fa5eeeedc626069e5addf099'


    def get_actor_id(api_key, actor_name):
        search_url = "https://api.themoviedb.org/3/search/person"

        params = {
            "api_key": api_key,
            "query": actor_name
        }

        response = requests.get(search_url, params=params)
        data = response.json()

        if data['results']:
            return data['results'][0]['id']
        else:
            return None

    def get_genre_id(api_key, genre_name):
        genres_url = "https://api.themoviedb.org/3/genre/movie/list"

        params = {
            "api_key": api_key,
            "language": "en-US"
        }

        response = requests.get(genres_url, params=params)
        data = response.json()

        for genre in data['genres']:
            if genre['name'].lower() == genre_name.lower():
                return genre['id']

        return None

    def get_movie_suggestions(api_key, genre_id, actor_id, min_rating, year):
        discover_url = "https://api.themoviedb.org/3/discover/movie"

        params = {
            "api_key": api_key,
            "with_genres": genre_id,
            "with_cast": actor_id,
            "vote_average.gte": min_rating,
            "primary_release_year": year,
            "sort_by": "popularity.desc"
        }

        if not actor_id:
            del params["with_cast"]

        response = requests.get(discover_url, params=params)
        data = response.json()
        if "results" in data:
            return [movie['id'] for movie in data["results"]]
                
    actor=get_actor_id(api, a)
    genre=get_genre_id(api, g)
    sp1=get_movie_suggestions(api, genre, actor, min_rating, year)
    sp2=[t[0] for t in doc]
    common_elements = list(set(sp1).intersection(sp2))
    if common_elements == []:
        return [t[0] for t in doc[:20]]
    sp1=[t for t in sp1 if t not in common_elements]
    common_elements = [t[0] for t in doc if t[0] in common_elements]#last change

    index1, index2 = 0, 0
    app=[]
    while index1 < len(sp1) or index2 < len(common_elements):
        if index1 < len(sp1):
            app.append(sp1[index1])
            index1 += 1
        if index2 < len(common_elements):
            app.append(common_elements[index2])
            index2 += 1

    return app
