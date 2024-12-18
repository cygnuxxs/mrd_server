# Documentation for Music Recommendation System

## Overview
This project is a Flask-based **Music Recommendation System**. It provides endpoints for recommending songs, fetching genres, searching for songs, and downloading music from YouTube. The system leverages machine learning models for song recommendations and integrates YouTube search functionality to retrieve metadata and download songs in MP3 format.

---

## Features
1. **Song Recommendations:** Suggests songs based on user-provided input, either by song name or feature values.
2. **Genre Fetching:** Retrieves songs by genre and searches for their details.
3. **Search Functionality:** Searches for songs on YouTube and returns metadata (e.g., title, views, duration).
4. **Music Downloading:** Downloads music from YouTube in MP3 format.

---

## Endpoints
### 1. `/download`
- **Method:** `POST`
- **Description:** Downloads a song from YouTube as an MP3 file.
- **Request Body:**
```json
{
  "videoId": "<YouTube Video ID>",
  "title": "<Song Title>"
}
```
- **Response:** Sends the MP3 file as a downloadable attachment.
- **Workflow:**
  1. Uses `yt-dlp` to download the song in the best audio quality.
  2. Converts the file to MP3 format with FFmpeg.
  3. Sends the file to the client and deletes it from the server after the request.

---

### 2. `/recommend_by_values`
- **Method:** `POST`
- **Description:** Recommends songs based on feature values like danceability, energy, etc.
- **Request Body:**
```json
{
  "danceability": 0.8,
  "energy": 0.7,
  "loudness": -5.0,
  "speechiness": 0.1,
  "acousticness": 0.3,
  "instrumentalness": 0.0,
  "liveness": 0.2,
  "valence": 0.5
}
```
- **Response:**
```json
[
  "Song 1",
  "Song 2",
  ...
]
```
- **Workflow:**
  1. Extracts and normalizes the input features.
  2. Calls `recommend_songs_by_value` from `model_knn`.
  3. Returns the recommended songs as a JSON array.

---

### 3. `/recommend`
- **Method:** `POST`
- **Description:** Recommends songs based on a given song name.
- **Request Body:**
```json
{
  "song_name": "<Song Name>"
}
```
- **Response:**
```json
[
  "Recommended Song 1",
  "Recommended Song 2",
  ...
]
```
- **Error Handling:** Returns a 400 error if the `song_name` is missing or a 500 error if the recommendation model fails.
- **Workflow:**
  1. Calls the `recommend_songs` function from the `model` module.
  2. Returns the recommended songs.

---

### 4. `/genre`
- **Method:** `POST`
- **Description:** Fetches songs by genre and retrieves their metadata.
- **Request Body:**
```json
{
  "genre": "<Genre Name>"
}
```
- **Response:**
```json
[
  {
    "title": "Song Title",
    "viewCount": "1.2M",
    "thumbnail": "<Thumbnail URL>",
    "duration": "3:45",
    "publishedTime": "2 years ago",
    "channelThumbnail": "<Channel Thumbnail URL>",
    "channelName": "Channel Name",
    "songUrl": "<Song URL>",
    "videoId": "<Video ID>"
  },
  ...
]
```
- **Workflow:**
  1. Retrieves a DataFrame of songs from `fetch_genre` in the `model` module.
  2. Uses multithreading to search for each song on YouTube.
  3. Returns a list of song metadata.

---

### 5. `/search`
- **Method:** `POST`
- **Description:** Searches for songs on YouTube and returns their metadata.
- **Request Body:**
```json
[
  "Song 1",
  "Song 2",
  ...
]
```
- **Response:**
```json
[
  {
    "title": "Song Title",
    "viewCount": "1.2M",
    "thumbnail": "<Thumbnail URL>",
    "duration": "3:45",
    "publishedTime": "2 years ago",
    "channelThumbnail": "<Channel Thumbnail URL>",
    "channelName": "Channel Name",
    "songUrl": "<Song URL>",
    "videoId": "<Video ID>"
  },
  ...
]
```
- **Workflow:**
  1. Accepts a list of song names in the request.
  2. Uses multithreading to call the `search` function for each song.
  3. Returns a list of song metadata.

---

## Helper Functions
### `search(song: str)`
- **Description:** Searches for a song on YouTube and returns its metadata.
- **Input:**
  - `song`: The name of the song to search for.
- **Output:**
```json
{
  "title": "Song Title",
  "viewCount": "1.2M",
  "thumbnail": "<Thumbnail URL>",
  "duration": "3:45",
  "publishedTime": "2 years ago",
  "channelThumbnail": "<Channel Thumbnail URL>",
  "channelName": "Channel Name",
  "songUrl": "<Song URL>",
  "videoId": "<Video ID>"
}
```
- **Error Handling:** Returns `None` if an error occurs.
- **Workflow:**
  1. Uses the `VideosSearch` class from `youtubesearchpython` to search for the song.
  2. Extracts metadata such as title, video ID, view count, etc.
  3. Returns the metadata as a dictionary.

---

## Dependencies
### Python Libraries
1. **Flask:** For building the REST API.
2. **Flask-CORS:** For enabling cross-origin resource sharing.
3. **yt-dlp:** For downloading YouTube videos.
4. **YouTube Search Python:** For searching YouTube videos.
5. **Concurrent Futures:** For multithreading.
6. **OS:** For file operations.

### External Modules
1. `model`: Contains the `recommend_songs` and `fetch_genre` functions for song recommendations and genre fetching.
2. `model_knn`: Contains the `recommend_songs_by_value` function for recommendations based on feature values.

---

## Running the Application
1. Install the required dependencies:
```bash
pip install flask flask-cors yt-dlp youtube-search-python
```
2. Start the Flask server:
```bash
python app.py
```
3. Access the API at `http://localhost:8000`.

---

## Notes
- Ensure that `model.py` and `model_knn.py` are present in the same directory as `app.py`.
- The YouTube MP3 download functionality requires FFmpeg to be installed on the server.

---

## Potential Improvements
1. **Authentication:** Add user authentication for personalized recommendations.
2. **Error Handling:** Improve error messages and validation for inputs.
3. **Scalability:** Deploy the app on a cloud platform for handling high traffic.
4. **Caching:** Cache YouTube search results to reduce API calls.

