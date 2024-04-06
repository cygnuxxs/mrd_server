from flask import Flask, request, jsonify, after_this_request, send_file
from model import recommend_songs, fetch_genre
from model_knn import recommend_songs_by_value
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from youtubesearchpython import VideosSearch

from yt_dlp import *
import os

app = Flask(__name__)
CORS(app)

@app.route('/download', methods = ['GET', 'POST'])
def download():
    data = request.get_json()
    videoId = data.get('videoId')
    title = data.get('title')
    url = f'https://www.youtube.com/watch?v={videoId}'

    ydl_options = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '320',
        }],
        'outtmpl' : videoId + '.%(ext)s',
    }
    with YoutubeDL(ydl_options) as ydl:
        ydl.download([url])
    
    @after_this_request
    def remove_file(response):
        os.remove(f'{videoId}.mp3')
        return response
    return send_file(f'{videoId}.mp3', as_attachment=True, download_name=f'{title}.mp3')

@app.route('/recommend_by_values', methods = ['POST'])
def recommend_by_value():
    data = request.get_json()
    for i in data:
        data[i] = float(data[i])
    selected_features = ['danceability', 'energy', 'loudness', 'speechiness',
                     'acousticness', 'instrumentalness', 'liveness', 'valence']    
    input_features = []
    for i in selected_features:
        input_features.append(data[i])
    recommended_songs = recommend_songs_by_value(input_features)
    print(recommended_songs)
    return jsonify(recommended_songs)


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    song_name = data.get('song_name')
    if not song_name:
        return jsonify({'error': 'Missing song name in request.'}), 400
    
    try:
        recommendations = recommend_songs(song_name)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/genre', methods = ["POST"])
def genre_fetch():
    response = request.get_json()
    genre_df = fetch_genre(response)

    data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search, song) for song in genre_df]
        for future in futures:
            result = future.result()
            if result:
                data.append(result)
    return jsonify(data)

@app.route('/search', methods=['POST'])
def search_handler():
    songs = request.get_json()
    if not songs:
        return jsonify({'error': 'No songs provided in request.'}), 400
    
    data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search, song) for song in songs]
        for future in futures:
            result = future.result()
            if result:
                data.append(result)
    return jsonify(data)

def search(song: str):
    try:
        req = VideosSearch(song, limit=1)
        response = req.result()['result'][0]

        title = response['title']
        videoId = response['id']
        viewCount = response['viewCount']['short']
        songThumbnailUrl = response['thumbnails'][0]['url']
        duration = response['duration']
        publishedTime = response['publishedTime']
        channelThumbnailUrl = response['channel']['thumbnails'][0]['url']
        songUrl = response['link']
        channelName = response['channel']['name']

        result = {
            'title': title,
            'viewCount': viewCount,
            'thumbnail': songThumbnailUrl,
            'duration': duration,
            'publishedTime': publishedTime,
            'channelThumbnail': channelThumbnailUrl,
            'channelName' : channelName,
            'songUrl': songUrl,
            'videoId' : videoId,
        }
        return result
    except Exception as e:
        print(f"Error searching for song: {e}")
        return None
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
