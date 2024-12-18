from pytubefix import Search, YouTube
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from utils import format_duration, format_published_time, format_view_count
from concurrent.futures import ThreadPoolExecutor
from model import fetch_genre, recommend_songs
from model_knn import recommend_songs_by_value
from fastapi.middleware.cors import CORSMiddleware
import io
import ffmpeg
from typing import List

app = FastAPI()
origins = [
    'http://localhost:5173'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SongRequest(BaseModel):
    song_name: str

class SongRecommendationRequest(BaseModel):
    danceability: float
    energy: float
    loudness: float
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float

class GenreRequest(BaseModel):
    genre_list: List[str]

class SearchResult(BaseModel):
    title: str
    viewCount: str
    thumbnail: str
    duration: str
    publishedTime: str
    channelThumbnail: str
    channelName: str
    songUrl: str
    videoId: str

class DownloadRequest(BaseModel):
    videoId : str
    songTitle : str


@app.post('/download')
async def download(request: DownloadRequest):
    videoId = request.videoId
    songTitle = request.songTitle
    print(videoId)
    url = f'https://www.youtube.com/watch?v={videoId}'
    
    try:
        # Create YouTube object using Pytube
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Download audio stream to a buffer (using ffmpeg to convert the stream)
        audio_buffer = io.BytesIO()

        # Use ffmpeg to process the audio stream and write it to a buffer
        # You can specify other parameters, such as the bitrate, audio codec, etc.
        process = (
            ffmpeg
            .input(audio_stream.url)
            .output('pipe:1', format='mp3', acodec='libmp3lame', audio_bitrate='192k')
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        # Read the processed audio data into the buffer
        audio_data = process.stdout.read()
        audio_buffer.write(audio_data)
        audio_buffer.seek(0)

        # Prepare response headers
        headers = {
            "Content-Disposition": f"attachment; filename={videoId}.mp3",
            "Content-Type": "audio/mp3"
        }

        return Response(content=audio_buffer.read(), media_type="audio/mp3", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.post('/recommend_by_values')
async def recommend_by_value(data: SongRecommendationRequest):
    selected_features = ['danceability', 'energy', 'loudness', 'speechiness',
                         'acousticness', 'instrumentalness', 'liveness', 'valence']

    input_features = [data.danceability, data.energy, data.loudness, data.speechiness,
                      data.acousticness, data.instrumentalness, data.liveness, data.valence]

    recommended_songs = recommend_songs_by_value(input_features)
    return recommended_songs


@app.post('/recommend')
async def recommend(data: SongRequest):
    song_name = data.song_name
    if not song_name:
        raise HTTPException(
            status_code=400, detail="Missing song name in request.")

    try:
        recommendations = recommend_songs(song_name)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/genre')
async def genre_fetch(data: GenreRequest):
    genre_df = fetch_genre(data.genre_list)
    data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search, song) for song in genre_df]
        for future in futures:
            result = future.result()
            if result:
                data.append(result)
    return data


@app.post('/search', response_model=List[SearchResult])
async def search_handler(songs: List[str]):
    if not songs:
        raise HTTPException(
            status_code=400, detail="No songs provided in request.")

    data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search, song) for song in songs]
        for future in futures:
            result = future.result()
            if result:
                data.append(result)
    return data


def search(song: str):
    try:
        search_results = Search(song).videos
        if not search_results:
            print(f"No results found for {song}")
            return None

        response = search_results[0]

        if not response.video_id or not response.title:
            print(f"Missing required info for {song}")
            return None

        title = response.title
        videoId = response.video_id
        viewCount = format_view_count(response.views)
        songThumbnailUrl = response.thumbnail_url
        duration = format_duration(response.length)
        publishedTime = format_published_time(response.publish_date)
        channelThumbnailUrl = response.channel_url
        songUrl = response.watch_url
        channelName = response.author

        result = {
            'title': title,
            'viewCount': viewCount,
            'thumbnail': songThumbnailUrl,
            'duration': duration,
            'publishedTime': publishedTime,
            'channelThumbnail': channelThumbnailUrl,
            'channelName': channelName,
            'songUrl': songUrl,
            'videoId': videoId,
        }
        return result
    except Exception as e:
        print(f"Error searching for song: {e}")
        return None