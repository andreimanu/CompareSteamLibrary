# 🎮 Steam Common Games Finder

Find which Steam games you and your friends have in common — with actual playtime, profile avatars, and game covers — directly in your browser.

This tool uses the Steam Web API and Streamlit to display shared games between multiple public Steam accounts.

---

## 🚀 Features

- ✅ Accepts vanity names, SteamID64, or full profile URLs
- ✅ Supports up to 10 users
- ✅ Detects and resolves public profiles automatically
- ✅ Shows:
  - 👤 Display name
  - 🖼️ Avatar
  - 🕒 Hours played
  - 🎮 Common games
  - 🖼️ Game cover image
- ✅ Sorts:
  - Games by total hours (descending)
  - Players by hours per game (descending)
- ✅ Tells how many common games were found

---

## 📦 Requirements

- Python 3.8+
- `streamlit`
- `requests`

Install locally:

```bash
pip install streamlit requests
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 🌐 Run Online (Streamlit Cloud)

1. Fork or upload this project to GitHub
2. Go to: https://streamlit.io/cloud
3. Click "New app"
4. Select the repo and set `app.py` as the entry point
5. Add your Steam API Key to Secrets:

```
STEAM_API_KEY = "your_steam_api_key_here"
```

6. Click Deploy and share your app

---

## 🔐 Steam API Key

You must generate a free API key from:

https://steamcommunity.com/dev/apikey

Paste it as a secret in `.streamlit/secrets.toml` or through the cloud interface.

---

## ✅ To Do / Ideas

- Export common games to CSV
- Filter by genre or multiplayer tags
- Show achievement overlap
- Compare playtime differences
- Highlight recent games only

---

## 📄 License

MIT License. Use freely, credit appreciated.
