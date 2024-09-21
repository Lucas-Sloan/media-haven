import requests
from decouple import config

GIANTBOMB_API_URL = 'https://www.giantbomb.com/api/'
GIANTBOMB_API_KEY = config('GIANTBOMB_API_KEY')
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


def fetch_giantbomb_game_data(title):
    """Fetch game data from GiantBomb API by title."""
    params = {
        'api_key': GIANTBOMB_API_KEY,
        'format': 'json',
        'query': title,
        'resources': 'game',
    }
    headers = {
        'User-Agent': 'MediaHaven Game Fetcher',
    }

    response = requests.get(GIANTBOMB_API_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        game_data = response.json()
        if game_data.get('status_code') == 1 and game_data.get('number_of_page_results', 0) > 0:
            game = game_data['results'][0]
            return {
                'title': game.get('name'),
                'genre': ', '.join([genre.get('name') for genre in game.get('genres', [])]) or 'Unknown',
                'description': game.get('deck', 'No description available'),
                'image_url': game.get('image', {}).get('small_url', ''),  # Safe access to avoid KeyError
            }
        else:
            print(f"GiantBomb API error: {game_data.get('error')}")
            return None  # No results found or error
    else:
        print(f"Error fetching data from GiantBomb: {response.status_code} - {response.text}")
        return None  # Handle network error or invalid response
