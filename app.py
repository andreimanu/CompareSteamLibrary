import requests
import streamlit as st

API_KEY = st.secrets["STEAM_API_KEY"]

def resolve_input_to_steamid(input_str):
    if input_str.isdigit() and len(input_str) >= 16:
        return input_str
    url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {'key': API_KEY, 'vanityurl': input_str}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        result = r.json()
        if result.get("response", {}).get("success") != 1:
            return None
        return result["response"].get("steamid")
    except Exception:
        return None

def get_display_name(steamid):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {'key': API_KEY, 'steamids': steamid}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        players = r.json().get('response', {}).get('players', [])
        return players[0]['personaname'] if players else steamid
    except Exception:
        return steamid

def get_owned_games(steamid):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': API_KEY,
        'steamid': steamid,
        'include_appinfo': True,
        'format': 'json'
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get('response', {})
        if 'games' not in data:
            return {}
        return {str(g['appid']): {
            'name': g['name'],
            'hours': round(g['playtime_forever'] / 60, 1)
        } for g in data['games']}
    except Exception:
        return {}

st.title("🎮 Steam Common Games Finder")
st.write("Start with 3 Steam users (vanity URL or SteamID64). More fields appear as needed (up to 10).")

user_inputs = []
max_fields = 10

# Inicializa con al menos 3 campos visibles, y muestra uno más si el último campo visible está lleno
for i in range(max_fields):
    if i < 3 or (i > 0 and user_inputs[-1]):
        u = st.text_input(f"User {i+1}", key=f"user_{i}")
        user_inputs.append(u)
    else:
        break

valid_inputs = [u for u in user_inputs if u.strip()]

if len(valid_inputs) >= 2:
    if st.button("Find Common Games"):
        steam_ids, display_names, user_games = [], [], []
        for u in valid_inputs:
            sid = resolve_input_to_steamid(u.strip())
            if not sid:
                st.error(f"Could not resolve user: {u}")
                st.stop()
            name = get_display_name(sid)
            games = get_owned_games(sid)
            if not games:
                st.error(f"No games found or profile private: {name}")
                st.stop()
            steam_ids.append(sid)
            display_names.append(name)
            user_games.append(games)

        common_ids = set(user_games[0].keys())
        for g in user_games[1:]:
            common_ids &= set(g.keys())

        if not common_ids:
            st.warning("No common games found.")
        else:
            results = []
            for appid in common_ids:
                name = user_games[0][appid]['name']
                hours = [user_games[i][appid]['hours'] for i in range(len(valid_inputs))]
                total = sum(hours)
                results.append((appid, name, hours, total))

            results.sort(key=lambda x: x[3], reverse=True)

            for appid, name, hours_list, _ in results:
                st.image(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg", width=308)
                st.markdown(f"### {name}")
                for i, h in enumerate(hours_list):
                    st.markdown(f"- **{display_names[i]}**: {h} hours")
                st.markdown("---")
