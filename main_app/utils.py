import requests
import logging
from decouple import config

CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')
API_KEY = config('OMDB_API_KEY')
IMDB_API_URL = 'https://api.igdb.com/v4/games'
OMDB_API_URL = 'http://www.omdbapi.com/'

def fetch_omdb_data(title):
    """Fetch media data from OMDB by title, works for movies, series (TV shows), etc."""
    params = {
        'apikey': API_KEY,
        't': title,  # 't' is the OMDB parameter for title search
    }
    response = requests.get(OMDB_API_URL, params=params)
    
    if response.status_code == 200:
        media_data = response.json()

        if media_data.get('Response') == 'True':  # Successful fetch
            # Extract media type and relevant information
            media_type = media_data.get('Type')
            
            if media_type in ['movie', 'series']:  # Handling for movies and TV shows
                return {
                    'title': media_data.get('Title'),
                    'media_type': media_type,  # Store the actual media type
                    'genre': media_data.get('Genre'),
                    'description': media_data.get('Plot'),
                    'image_url': media_data.get('Poster'),
                    'rating': media_data.get('imdbRating'),  # Optional: fetch IMDb rating
                    'status': None,  # Status would be set by user later
                }
            else:
                # If it's a type you want to ignore or not handle, you can return None
                return None
        else:
            return None  # Media not found or some other error
    else:
        return None  # Handle network error or invalid response

# Function to get OAuth token from Twitch API
def get_igdb_token():
    """
    Fetch the OAuth token from Twitch to authenticate with IGDB API.
    """
    client_id = config('CLIENT_ID')
    client_secret = config('CLIENT_SECRET')
    token_url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_url, data=data)
    
    # Handle possible errors
    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.text}")
    
    token_data = response.json()
    return token_data['access_token']

def fetch_game_data(game_title):
    """
    Fetch game data from IGDB by game title.
    """
    token = get_igdb_token()
    headers = {
        'Client-ID': config('CLIENT_ID'),
        'Authorization': f'Bearer {token}'
    }
    url = 'https://api.igdb.com/v4/games'
    body = f'fields name, genres.name, summary, cover.image_id; where name ~ "{game_title}";'
    
    response = requests.post(url, headers=headers, data=body)
    
    # Handle possible errors
    if response.status_code != 200:
        raise Exception(f"Failed to fetch game data: {response.text}")
    
    games = response.json()
    
    for game in games:
        if 'cover' in game and 'image_id' in game['cover']:
            image_id = game['cover']['image_id']
            game['cover']['url'] = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
    
    return games