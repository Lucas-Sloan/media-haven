import requests
from decouple import config


OMDB_API_URL = 'http://www.omdbapi.com/'
API_KEY = config('OMDB_API_KEY')  # Get the API key from environment variables

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

GIANTBOMB_API_URL = 'https://www.giantbomb.com/api/search/'
GIANTBOMB_API_KEY = config('GIANTBOMB_API_KEY')

def fetch_giantbomb_game_data(title):
    """Fetch game data from GiantBomb API by title."""
    params = {
        'api_key': GIANTBOMB_API_KEY,
        'format': 'json',
        'query': title,
        'resources': 'game',  # We're only searching for games
    }
    headers = {
        'User-Agent': 'MediaHaven Game Fetcher',  # GiantBomb requests that you send a User-Agent
    }

    response = requests.get(GIANTBOMB_API_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        game_data = response.json()
        if game_data['status_code'] == 1 and game_data['number_of_page_results'] > 0:
            # If there are results, return the first result or map through multiple
            game = game_data['results'][0]
            return {
                'title': game['name'],
                'genre': ', '.join([genre['name'] for genre in game['genres']]) if 'genres' in game else 'Unknown',
                'description': game.get('deck', 'No description available'),  # The brief summary of the game
                'image_url': game['image']['small_url'] if 'image' in game else '',  # Small image URL
            }
        else:
            return None  # No results found
    else:
        return None  # Handle network error or invalid response