import os
import requests
from dotenv import load_dotenv

# --- Load .env ---
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY must be set in .env")

TMDB_BASE = "https://api.themoviedb.org/3"

# --- TMDB Client ---
class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, endpoint, params=None):
        params = params.copy() if params else {}
        params["api_key"] = self.api_key
        try:
            resp = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return None

    def _fmt(self, m):
        return f"{m.get('title')} ({(m.get('release_date') or '????')[:4]}): {m.get('overview', '')[:200]}..."

    def search_movies(self, query):
        data = self._get("/search/movie", {"query": query})
        if not data:
            return ["Error searching movies. Please try again."]
        return [self._fmt(m) for m in data.get("results", [])]

    def discover_by_genre(self, genre):
        genres = self._get("/genre/movie/list")
        if not genres:
            return ["Error fetching genres. Please try again."]
        
        genres = genres.get("genres", [])
        genre_id = next((g["id"] for g in genres if g["name"].lower() == genre.lower()), None)
        if not genre_id:
            return [f"Genre '{genre}' not found."]
        
        data = self._get("/discover/movie", {"with_genres": genre_id, "sort_by": "popularity.desc"})
        if not data:
            return ["Error discovering movies. Please try again."]
        return [self._fmt(m) for m in data.get("results", [])]

    def movie_details(self, movie_id):
        try:
            # Ensure movie_id is a valid integer
            movie_id = int(movie_id)
            if movie_id <= 0:
                return "Invalid movie ID. Please provide a positive integer."
                
            data = self._get(f"/movie/{movie_id}")
            if not data:
                return f"Movie with ID {movie_id} not found. Please check the ID and try again."
                
            return f"{data.get('title', 'Unknown Title')} ({data.get('release_date', 'Unknown Year')[:4]}): {data.get('overview', 'No overview available.')}"
        except ValueError:
            return "Invalid movie ID format. Please provide a valid integer ID."
        except Exception:
            return f"Error retrieving details for movie ID {movie_id}. Please try again."

# Initialize TMDB client
tmdb = TMDBClient(TMDB_API_KEY)

# --- Tools ---
from langchain.agents import Tool

tools = [
    Tool(name="search_movies", func=lambda q: "\n".join(tmdb.search_movies(q)),
         description="Search movies by name or keywords."),
    Tool(name="discover_genre", func=lambda g: "\n".join(tmdb.discover_by_genre(g)),
         description="Discover popular movies by genre."),
    Tool(name="movie_details", func=lambda mid: tmdb.movie_details(mid),
         description="Get movie details by TMDB ID."),
]
