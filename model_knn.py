import pandas as pd
from sklearn.neighbors import NearestNeighbors
import numpy as np

import warnings

warnings.filterwarnings('ignore')

df = pd.read_csv('dataset.csv')
df.drop(columns=df.columns[0], axis=1, inplace=True)
df.drop_duplicates(['track_id'], inplace=True)
df.sort_values('popularity', ascending=False, inplace=True)
df = df[:10000]

selected_features = ['danceability', 'energy', 'loudness', 'speechiness',
                     'acousticness', 'instrumentalness', 'liveness', 'valence']
X = df[selected_features]
X_normalized = (X - X.mean()) / X.std()

knn_model = NearestNeighbors(n_neighbors=11, algorithm='brute', metric='euclidean')
knn_model.fit(X_normalized)

def recommend_songs_by_value(features):
    normalized_features = (features - X.mean()) / X.std()
    _, indices = knn_model.kneighbors([normalized_features])
    recommended_songs = df.iloc[indices[0]]
    concatenated_df = recommended_songs['track_name'] + ' by ' + recommended_songs['artists']
    return list(concatenated_df)