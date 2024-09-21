import requests
import logging
from decouple import config

RAWG_API_KEY = config('RAWG_API_KEY')
API_KEY = config('OMDB_API_KEY')
RAWG_API_URL = 'https://api.rawg.io/api/games'
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


def fetch_rawg_game_data(title):
    """Fetch game data from RAWG API by title."""
    params = {
        'key': RAWG_API_KEY,
        'page_size': 5,
        'search': title,
    }
    headers = {
        'User-Agent': 'MediaHaven Game Info Fetcher',
    }

    try:
        response = requests.get(RAWG_API_URL, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        game_data = response.json()  # Attempt to decode JSON

        # Log the fetched game data for debugging
        logging.info(f"RAWG API response for '{title}': {game_data}")

        if game_data.get('results'):  # Check if there are results
            game = game_data['results'][0]
            return {
                'title': game.get('name', 'Unknown'),
                'genre': ', '.join(genre['name'] for genre in game.get('genres', [])) or 'Unknown',
                'description': game.get('description_raw', game.get('description', 'No description available')),  # Check for description_raw
                'image_url': game.get('background_image', ''),  # Background image URL
            }
        else:
            logging.error(f"No results found for query: {title}. API response: {game_data}")
            return None  # No results found or API error
            
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - URL: {response.url}")
        return None  # Handle HTTP errors
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request exception occurred: {req_err}")
        return None  # Handle request errors
    except ValueError as json_err:
        logging.error(f"JSON decode error: {json_err}")
        return None  # Handle JSON decode errors