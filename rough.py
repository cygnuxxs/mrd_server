from pytubefix import Search

search = Search('Shape of You').videos

result = {
            'title': search[0].title,
            'viewCount': search[0].views,
            'thumbnail': search[0].thumbnail_url,
            'duration': search[0].length,
            'publishedTime': search[0].publish_date,
            'channelThumbnail': search[0].channel_url,
            'channelName': search[0].author,
            'songUrl': search[0].watch_url,
            'videoId': search[0].video_id,
        }
print(result)