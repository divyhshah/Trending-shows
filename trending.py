import pandas as pd
from datetime import datetime
import requests
import urllib
from flask import request
import json
from requests.exceptions import ConnectionError
import ast

## Get hashbale dictionary in terms of tuple 
class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

## Get output dictionary
def get_trending():
    qp = hashabledict(request.args)
    return {"data": _get_trending(qp)}

def _get_trending(qp):
    
    media = qp.get("media") or "movie"
    timewindow = qp.get("timewindow") or 'day'

    path = "https://api.themoviedb.org/3/"
    img_url = "https://image.tmdb.org/t/p/w500"

    api = '3f5c5b3fe404cdf71e5ea07fbc5daf22'
    find  = "trending"
    parameter_dict = {'api_key': api}
    get_url = path+find+'/'+media+'/'+timewindow+'?' + urllib.parse.urlencode(parameter_dict)

    try:
        r = requests.get(get_url, timeout=1)
    except ConnectionError as e:
        print(e)
        r = None
    
    

    
    if (media=='tv'):

        if r:
            response_dict = json.loads(r.text)
            df = pd.json_normalize(response_dict['results'], sep="_")
        else:
            result = {}

        COLS = ['original_name', 'first_air_date', 'vote_average', 'vote_count', 'popularity', 'media_type', 'poster_path']
        df.poster_path = img_url + df.poster_path
        df = df[COLS]
        df.rename(columns={'original_name': 'Title', 'vote_average': 'AvgVote', \
                        'vote_count': 'VoteCount', 'first_air_date': 'ReleaseDate','popularity': 'Popularity', 'poster_path': 'URL'}, inplace=True) #'release_date': 'ReleaseDate', 
        df = df.sort_values('Popularity', ascending=False)
    elif (media=='movie'):

        if r:
            response_dict = json.loads(r.text)
            df = pd.json_normalize(response_dict['results'], sep="_")
        else:
            result = {}

        COLS = ['title', 'release_date', 'vote_average', 'vote_count', 'popularity', 'media_type', 'poster_path']
        
        df.poster_path = img_url + df.poster_path
        df = df[COLS]
        df.rename(columns={'title': 'Title', 'vote_average': 'AvgVote', \
                        'vote_count': 'VoteCount', 'release_date': 'ReleaseDate' ,'popularity': 'Popularity', 'poster_path': 'URL'}, inplace=True) #'release_date': 'ReleaseDate', 
        df = df.sort_values('Popularity', ascending=False)
    elif(media=='person'):

        if r:
            response_dict = json.loads(r.text)
            df = pd.json_normalize(response_dict['results'], sep="_")
        else:
            result = {}

        
        person = []
        for ix, item in df.iterrows():
            dic = {"id": item.id}
            try:
                vcat = item.known_for
                for x in vcat:
                    dic["AvgVote"] = x["vote_average"]
            except ValueError:
                pass
            except Exception as ex:
                print(type(ex).__name__)
            person.append(dic)

        df_p = pd.DataFrame(person)
        COLS = ['name', 'known_for_department', 'profile_path', 'popularity', 'id']
        
        df.profile_path = img_url + df.profile_path
        df = df[COLS]
        df = df.merge(df_p, on='id', how='left')
        df.rename(columns={'name': 'Title', 'profile_path': 'URL', 'known_for_department': 'KnownFor', 'popularity': 'Popularity'}, inplace=True)

        df = df.sort_values('Popularity', ascending=False)

    result = df.head(10).to_dict(orient='records')
    return result
