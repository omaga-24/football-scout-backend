import httpx
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

async def get_player_suggestions(name: str):
    """
    Fetch player suggestions using path-based parameters.
    Handles 'players' key based on actual API response.
    """
    host = "sportapi7.p.rapidapi.com"

    # URL encode the name to handle spaces and special characters safely
    safe_name = urllib.parse.quote(name)
    url = f"https://{host}/api/v1/search/players/{safe_name}/more"

    headers = {
        "x-rapidapi-key": os.getenv("FOOTBALL_API_KEY"),
        "x-rapidapi-host": host,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)

            print(f"📡 Requesting: {url}")
            print(f"📡 Status Code: {response.status_code}")

            if response.status_code != 200:
                return []

            data = response.json()

            # This is the most critical logic change!
            # Based on the API logs, the response contains a 'players' list.
            if "players" in data:
                return data.get("players", [])

            return []

        except Exception as e:
            print(f"❌ SportAPI Exception: {str(e)}")
            return []