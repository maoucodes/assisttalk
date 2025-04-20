from flask import Flask, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
import random

app = Flask(__name__)
CORS(app)

API_KEY = 'AIzaSyDO_RMlMevaTD5KHAeY415sKJLqWqrf0mQ'
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_info(video_id):
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    )
    response = request.execute()
    
    if not response['items']:
        return None
        
    item = response['items'][0]
    return {
        'title': item['snippet']['title'],
        'views': item['statistics'].get('viewCount', 0),
        'likes': item['statistics'].get('likeCount', 0),
        'channel': item['snippet']['channelTitle'],
        'video_id': item['id'],
        'thumbnail': item['snippet']['thumbnails']['high']['url']  # Add this line
    }

def get_trending_videos():
    request = youtube.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode='US',
        maxResults=50
    )
    
    response = request.execute()
    
    videos = []
    for item in response['items']:
        video_data = {
            'title': item['snippet']['title'],
            'video_id': item['id'],
            'views': item['statistics'].get('viewCount', 0),
            'likes': item['statistics'].get('likeCount', 0),
            'channel': item['snippet']['channelTitle'],
            'thumbnail': item['snippet']['thumbnails']['high']['url']  # Add this line
        }
        videos.append(video_data)
    return videos


@app.route('/random')
def random_videos():
    try:
        videos = get_trending_videos()
        random_selection = random.sample(videos, min(5, len(videos)))
        return jsonify(random_selection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trending')
def trending_videos():
    try:
        videos = get_trending_videos()
        return jsonify(videos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/info/<video_id>')
def video_info(video_id):
    try:
        info = get_video_info(video_id)
        if info is None:
            return jsonify({'error': 'Video not found'}), 404
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/search/<query>')
def search_videos(query):
        try:
            request = youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=10
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                video_id = item['id']['videoId']
                video_info = get_video_info(video_id)
                if video_info:
                    videos.append(video_info)
            return jsonify(videos)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
