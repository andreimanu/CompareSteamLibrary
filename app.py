import requests
import streamlit as st

# Validate Steam API key immediately
API_KEY = st.secrets.get("STEAM_API_KEY", "").strip()
st.text(f"API_KEY loaded (len={len(API_KEY)}): starts with {API_KEY[:5]}")
if not API_KEY or API_KEY == "YOUR_STEAM_API_KEY_HERE":
    st.error("❌ Steam API key is missing or invalid. Check your app secrets.")
    st.stop()

def resolve_input_to_steamid(input_str):
    if input_str.isdigit() and len(input_str) >= 16:
        return input_str
    url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {'key': API_KEY, 'vanityurl': input_str}
    try:
        r = requests.get(url, params=params, timeout=5)
        st.text(f"[ResolveVanityURL] Status: {r.status_code}")
        st.text(f"[ResolveVanityURL] Response: {r.text}")
        r.raise_for_status()
        result = r.json()
        success = result.get("response", {}).get("success")
        if success != 1:
            st.warning(f"Steam API response: success={success} for user '{input_str}'")
            return None
        return result["response"].get("steamid")
    except Exception as e:
        st.error(f"[ResolveVanityURL] Exception: {e}")
        return None

def get_display_name(steamid):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {'key': API_KEY, 'steamids': steamid}
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        return r.json().get('response', {}).get('players', [{}])[0].get("personaname", steamid)
    except Exception as e:
        st.error(f"[GetPlayerSummaries] Exception: {e}")
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
        return {
            str(g['appid']): {
                'name': g['name'],
                'hours': round(g['playtime_forever'] / 60, 1)
            }
            for g in r.json().get('response', {}).get('games', [])
        }
    except Exception as e:
        st.error(f"[GetOwnedGames] Exception: {e}")
        return {}

st.title("🎮 Steam Common Games Finder — DEBUG MODE")
st.write("This version shows full API errors and responses for debugging.")

user_inputs = []
max_fields = 10
for i in range(max_fields):
    if i < 3 or (i > 0 and user_inputs[-1]):
        u = st.text_input(f"User {i+1}", key=f"user_{i}")
        user_inputs.append(u)
    else:
        break

valid_inputs = [u for u in user_inputs if u.strip()]

if len(valid_inputs) >= 1:
    if st.button("Test Resolution Only"):
        for u in valid_inputs:
            sid = resolve_input_to_steamid(u.strip())
            if sid:
                st.success(f"✔ '{u}' resolved to SteamID64: {sid}")
            else:
                st.error(f"❌ Could not resolve '{u}'")
