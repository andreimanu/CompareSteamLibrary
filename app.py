import requests
import streamlit as st

API_KEY = st.secrets.get("STEAM_API_KEY", "").strip()
if not API_KEY:
    st.error("❌ Steam API key is missing or invalid. Check your app secrets.")
    st.stop()

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

def get_user_profile(steamid):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {'key': API_KEY, 'steamids': steamid}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        players = r.json().get('response', {}).get('players', [])
        if not players:
            return {'name': steamid, 'avatar': '', 'steamid': steamid}
        player = players[0]
        return {
            'name': player.get('personaname') or steamid,
            'avatar': player.get('avatarfull', ''),
            'steamid': steamid
        }
    except Exception:
        return {'name': steamid, 'avatar': '', 'steamid': steamid}

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
        return {
            str(g['appid']): {
                'name': g['name'],
                'hours': round(g['playtime_forever'] / 60, 1)
            } for g in data['games']
        }
    except Exception:
        return {}

# UI
st.title("🎮 Steam Common Games Finder")
st.write("Enter up to 10 Steam profile names (vanity URLs or SteamID64). Only non-empty fields are used.")

user_inputs = [st.text_input(f"User {i+1}", key=f"user_{i}") for i in range(10)]
valid_inputs = [u.strip() for u in user_inputs if u.strip()]

if len(valid_inputs) >= 2:
    if st.button("Find Common Games"):
        profiles = []
        user_games = []

        for u in valid_inputs:
            sid = resolve_input_to_steamid(u)
            if not sid:
                st.error(f"❌ Could not resolve user: {u}")
                st.stop()
            profile = get_user_profile(sid)
            games = get_owned_games(sid)
            if not games:
                st.error(f"❌ No games found or profile private: {profile['name']}")
                st.stop()
            profiles.append(profile)
            user_games.append(games)

        # Match common appIDs
        common_ids = set(user_games[0].keys())
        for g in user_games[1:]:
            common_ids &= set(g.keys())

        if not common_ids:
            st.warning("⚠️ No common games found.")
        else:
            results = []
            for appid in common_ids:
                name = user_games[0][appid]['name']
                hours_data = []
                for i in range(len(profiles)):
                    h = user_games[i][appid]['hours']
                    hours_data.append({
                        'name': profiles[i]['name'],
                        'avatar': profiles[i]['avatar'],
                        'hours': h
                    })
                hours_data.sort(key=lambda x: x['hours'], reverse=True)
                results.append((appid, name, hours_data))

            # Sort games by total hours descending
            results.sort(key=lambda x: sum(u['hours'] for u in x[2]), reverse=True)

            for appid, name, user_data in results:
                st.image(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg", width=308)
                st.markdown(f"### {name}")
                for user in user_data:
                    cols = st.columns([1, 5])
                    if user['avatar']:
                        cols[0].image(user['avatar'], width=50)
                    cols[1].markdown(f"**{user['name']}**: {user['hours']} hours")
                st.markdown("---")
else:
    st.info("Please enter at least 2 users.")
