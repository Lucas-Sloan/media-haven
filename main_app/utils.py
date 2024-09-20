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
