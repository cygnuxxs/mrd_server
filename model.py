import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from fuzzywuzzy import process
df = pd.read_csv('dataset.csv')
df.drop(df.columns[0], axis=1, inplace=True)
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

tracks = df.drop(['track_id', 'duration_ms'], axis=1)
tracks = tracks.sort_values('popularity', ascending=False)[:5000]
tracks.drop_duplicates(subset=['track_name'], keep='first', inplace=True)
tracks = tracks.drop(['mode', 'time_signature'], axis=1)

song_vectorizer = CountVectorizer()
song_vectorizer.fit(tracks['track_genre'])

def get_similarities(song_name, data):
    text_array1 = song_vectorizer.transform(data[data['track_name'] == song_name]['track_genre']).toarray()
    num_array1 = data[data['track_name'] == song_name].select_dtypes(include=np.number).to_numpy()

    similarities = []
    for index, row in data.iterrows():
        name = row['track_name']
        
        text_array2 = song_vectorizer.transform(data[data['track_name']==name]['track_genre']).toarray()
        num_array2 = data[data['track_name']==name].select_dtypes(include=np.number).to_numpy()

        text_sim = cosine_similarity(text_array1, text_array2)[0][0]
        num_sim = cosine_similarity(num_array1, num_array2)[0][0]
        similarities.append(text_sim + num_sim)
    return similarities

from fuzzywuzzy import process


def recommend_songs(song_name, data=tracks):
    # Base case
    similar_strings = process.extract(song_name, tracks['track_name'], limit=1)
    if similar_strings[0][1] < 88:
        print('This song is either not so popular or you\
        have entered invalid_name.\n Some songs you may like:\n')

        for song in data.sample(n=5)['track_name'].values:
            print(song)
        songs = data.sample(n=10)

        return [song_name] + list(songs['track_name'].iloc[0:11] + ' by ' + songs['artists'].iloc[0:11])

    extracted_song_name = similar_strings[0][0]
    data['similarity_factor'] = get_similarities(extracted_song_name, data)

    data.sort_values(by=['similarity_factor', 'popularity'],
                     ascending=[False, False],
                     inplace=True)
    return list(data['track_name'].iloc[0:11] + ' by ' + data['artists'].iloc[0:11])


def fetch_genre(genre_name):
    genre_df = df[(df['track_genre'] == genre_name) & (df['popularity'] > 30)]
    data = genre_df.sample(11)
    return list(data['track_name'] + ' by ' + data['artists'])
