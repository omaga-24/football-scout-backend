from fastapi import APIRouter, HTTPException
from app.db.mongodb import db_helper
from app.services.football_api import get_player_suggestions

router = APIRouter()

# 💡 Global Cache (Persists only while the server is running)
suggestion_cache = {}

@router.get("/scout/{name}")
async def scout_player(name: str):
    try:
        # 1. Check if this player already exists in the MongoDB database
        existing_player = await db_helper.db.players.find_one({"name": {"$regex": name, "$options": "i"}})
        if existing_player:
            existing_player["_id"] = str(existing_player["_id"])
            return {"status": "success", "source": "database", "data": existing_player}

        # 2. If not in DB, fetch suggestions from the External API
        players_list = await get_player_suggestions(name)
        if not players_list:
            raise HTTPException(status_code=404, detail="No players found for this name.")

        best_match = players_list[0]
        team_data = best_match.get("team", {})

        new_player_data = {
            "player_id": str(best_match.get("id")),
            "name": best_match.get("name"),
            "team_name": team_data.get("name", "No Club"),
            "team_logo_url": f"https://api.sofascore.app/api/v1/team/{team_data.get('id')}/image" if team_data.get("id") else "No Team Logo",
            "country": best_match.get("country", {}).get("name", "Unknown"),
            "position": best_match.get("position", "N/A"),
            "jersey_number": best_match.get("jerseyNumber", "N/A"),
            "user_count": best_match.get("userCount", 0),
            "image_url": f"https://api.sofascore.app/api/v1/player/{best_match.get('id')}/image"
        }

        # 3. Save the new player data into the Database for future requests
        result = await db_helper.db.players.insert_one(new_player_data)
        new_player_data["_id"] = str(result.inserted_id)

        return {"status": "success", "source": "api", "data": new_player_data}
    except Exception as e:
        print(f"🚨 Scout Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/suggestions/{name}")
async def get_suggestions(name: str):
    name_key = name.lower().strip()

    # --- Step 1: Check Memory Cache ---
    if name_key in suggestion_cache:
        print(f"✅ Suggestion Cache Hit: {name_key}")
        return suggestion_cache[name_key]

    # --- Step 2: Suggest players already existing in MongoDB ---
    try:
        db_players = await db_helper.db.players.find(
            {"name": {"$regex": f"^{name}", "$options": "i"}}
        ).limit(5).to_list(length=5)

        if db_players:
            results = [{
                "id": p.get("player_id"),
                "name": p.get("name"),
                "team": p.get("team_name")
            } for p in db_players]

            # Cache the results from DB as well
            suggestion_cache[name_key] = results
            print(f"📂 Suggestions from DB: {name_key}")
            return results
    except Exception as e:
        print(f"⚠️ DB Search Error: {e}")

    # --- Step 3: Request from RapidAPI if not found locally ---
    print(f"📡 Requesting RapidAPI for: {name_key}")
    try:
        # Note: If get_player_suggestions returns an empty list (due to 429 errors), we handle it here
        players_list = await get_player_suggestions(name)

        if not players_list:
            return []

        suggestions_list = []
        for p in players_list[:5]:
            suggestions_list.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "team": p.get("team", {}).get("name", "No Club")
            })

        # Cache the suggestions only if the API request was successful
        if suggestions_list:
            suggestion_cache[name_key] = suggestions_list

        return suggestions_list

    except Exception as e:
        print(f"🚨 API Suggestions Error: {e}")
        # Return an empty list instead of crashing to prevent front-end errors
        return []