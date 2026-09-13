import os, sys, json, csv, re, urllib.parse
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r"I:\sikander-os"
DATA_DIR = os.path.join(ROOT_DIR, "data", "music")
EXPORT_DIR = os.path.join(DATA_DIR, "spotify_exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

LIBRARY_JSON = os.path.join(DATA_DIR, "sikander_music_library.json")
with open(LIBRARY_JSON, "r", encoding="utf-8") as f:
    library_data = json.load(f)

tracks = library_data.get("tracks", [])
metadata = library_data.get("metadata", {})

print(f"Loaded {len(tracks)} tracks from master library.")

# Define Collections / Playlists
MOOD_COLLECTIONS = {
    "01_Sunset_Deep_House": {
        "title": "Sikander — 🌅 Sunset Deep House",
        "desc": "Warm saxophone melodic house, deep rolling basslines, and euphoric sunset dopamine.",
        "filter": lambda t: t.get("category") == "Sunset Deep House" or t.get("mood") == "Sunset Deep House"
    },
    "02_Hypnotic_Trance": {
        "title": "Sikander — 🌌 Hypnotic Trance & Balearic",
        "desc": "Expansive progressive synth arpeggios, ethereal breakdowns, and late-night highway flow state.",
        "filter": lambda t: t.get("category") == "Hypnotic Trance & Balearic" or t.get("mood") == "Hypnotic Trance"
    },
    "03_Gym_Peak_Energy": {
        "title": "Sikander — ⚡ Gym Peak Energy",
        "desc": "Relentless 4-on-the-floor kick, explosive drops, driving cadence (126-132 BPM), and PR workout motivation.",
        "filter": lambda t: t.get("category") == "Gym Peak Energy" or t.get("mood") == "Gym / High Energy"
    },
    "04_Desi_Heritage_Sufi": {
        "title": "Sikander — 🪕 Desi Heritage & Melodic Sufi",
        "desc": "Soul-piercing South Asian classical/qawwali vocals, Pakistani rock guitars, and cultural nostalgia.",
        "filter": lambda t: t.get("category") == "Desi Heritage & Sufi" or t.get("mood") == "Desi Soul & Sufi" or t.get("is_desi")
    },
    "05_Buddha_Bar_Lounge": {
        "title": "Sikander — ☕ Buddha Bar & World Lounge",
        "desc": "Serene downtempo world groove, ethnic acoustic strings, sitar, and evening contemplative zen.",
        "filter": lambda t: t.get("category") == "Buddha Bar Lounge" or t.get("mood") == "Buddha Bar Lounge"
    },
    "06_Retro_Dance_Rock": {
        "title": "Sikander — 🎸 Retro Dance & Pop-Rock",
        "desc": "Timeless 90s-2000s singalong hooks, nostalgic millennial Eurodance, and melodic alt-rock classics.",
        "filter": lambda t: t.get("category") == "Retro Dance & Pop-Rock" or t.get("mood") == "Retro Dance & Pop-Rock"
    },
    "00_Top_Taste_Picks_Liked": {
        "title": "Sikander — ⭐ Top Taste Picks & Liked (90%+)",
        "desc": "Highest conviction tracks across all pillars: Spotify Liked songs and 90%+ mathematical taste matches.",
        "filter": lambda t: t.get("in_spotify_liked") or t.get("taste_match", 0) >= 90
    },
    "00_All_Manual_Downloads": {
        "title": "Sikander — 📁 All Manual Downloads (1,219 Tracks)",
        "desc": "100% handpicked choices: Root direct singles, Year-Month monthly folders (2016-2020), and Desi Heritage collection.",
        "filter": lambda t: t.get("is_manual_download")
    },
    "00_Root_Direct_Singles": {
        "title": "Sikander — 💾 Root Direct Singles (435 Tracks)",
        "desc": "Standalone individual songs downloaded directly to the root of I:\\Music over the years.",
        "filter": lambda t: t.get("is_root_manual") or (t.get("source_folder") == "Root")
    },
    "00_Master_Library_All": {
        "title": "Sikander — 🔀 Master Library (Shuffle All)",
        "desc": f"Complete deduplicated archive of {len(tracks)} tracks for seamless random shuffle across all moods.",
        "filter": lambda t: True
    }
}

manifest = {}

for key, config in MOOD_COLLECTIONS.items():
    matched = [t for t in tracks if config["filter"](t)]
    # Sort by taste match descending, then artist, then title
    matched.sort(key=lambda t: (-t.get("taste_match", 0), t.get("artist", "").lower(), t.get("title", "").lower()))
    
    spotify_matched_count = sum(1 for t in matched if t.get("spotify_id"))
    
    csv_file = os.path.join(EXPORT_DIR, f"{key}.csv")
    txt_file = os.path.join(EXPORT_DIR, f"{key}.txt")
    m3u_file = os.path.join(EXPORT_DIR, f"{key}.m3u8")
    
    # 1. Write CSV for TuneMyMusic / Soundiiz / Excel
    with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Track name", "Artist name", "Album name", "Spotify ID", "Spotify URL", "Taste Match", "Mood", "Local Filename"])
        for t in matched:
            writer.writerow([
                t.get("title", ""),
                t.get("artist", ""),
                t.get("source_folder", ""),
                t.get("spotify_id") or "",
                t.get("spotify_url") or "",
                f"{t.get('taste_match', 75)}%",
                t.get("mood", ""),
                t.get("raw_filename", "")
            ])
            
    # 2. Write TXT for TuneMyMusic / Soundiiz "From Text" or clipboard paste
    with open(txt_file, "w", encoding="utf-8") as f:
        for t in matched:
            f.write(f"{t.get('artist')} - {t.get('title')}\n")

    # 3. Write URIs file for direct Ctrl+V copy-paste into Spotify Desktop
    uris_file = os.path.join(EXPORT_DIR, f"{key}_uris.txt")
    with open(uris_file, "w", encoding="utf-8") as f:
        for t in matched:
            if t.get("spotify_uri"):
                f.write(f"{t.get('spotify_uri')}\n")
                
    # 4. Write M3U8 for Spotify Local Files, VLC, Foobar2000, Windows Media Player
    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"#PLAYLIST:{config['title']}\n\n")
        for t in matched:
            f.write(f"#EXTINF:-1,{t.get('artist')} - {t.get('title')}\n")
            folder = t.get("source_folder", "Root")
            if folder == "Root":
                fpath = os.path.join(r"I:\Music", t.get("raw_filename", ""))
            else:
                fpath = os.path.join(r"I:\Music", folder, t.get("raw_filename", ""))
            f.write(f"{fpath}\n\n")
            
    manifest[key] = {
        "title": config["title"],
        "description": config["desc"],
        "track_count": len(matched),
        "spotify_matched_count": spotify_matched_count,
        "csv_filename": f"{key}.csv",
        "txt_filename": f"{key}.txt",
        "uris_filename": f"{key}_uris.txt",
        "m3u_filename": f"{key}.m3u8"
    }
    print(f"Exported [{key}]: {len(matched)} tracks ({spotify_matched_count} with Spotify IDs).")

# Write manifest JSON
manifest_file = os.path.join(EXPORT_DIR, "export_manifest.json")
with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump({
        "generated_at": metadata.get("generated_at", "2026-09-13T01:50:00+05:00"),
        "total_library_tracks": len(tracks),
        "collections": manifest
    }, f, indent=2, ensure_ascii=False)

# Write comprehensive guide
guide_file = os.path.join(EXPORT_DIR, "SPOTIFY_IMPORT_GUIDE.md")
guide_content = f"""# 🎧 COMPLETE GUIDE: HOW TO ADD & CATEGORIZE SIKANDER'S MUSIC IN SPOTIFY

> **Goal:** Add your liked and manually downloaded songs from `I:\\Music` to Spotify, properly categorized into Mood Playlists so you can either **play what you are in the mood for** OR **play all songs randomly**.

---

## ⚡ THE 3 WAYS TO USE YOUR MUSIC IN SPOTIFY

| Method | Best For | Setup Time | Pros |
| :--- | :--- | :---: | :--- |
| **Method 1: Cloud Streaming Playlists (TuneMyMusic / Soundiiz)** | Streaming everywhere (Phone, Car, TV, Web) without phone storage | **60 Seconds** | No local files needed on phone; plays at top 320kbps cloud streaming quality. |
| **Method 2: Spotify Desktop Direct Paste (for Spotify-matched tracks)** | Instant 1-click addition to Spotify Desktop without any third-party web tool | **10 Seconds** | Copy URIs from the Hub and press `Ctrl + V` in Spotify Desktop. |
| **Method 3: Spotify "Local Files" (Native Desktop & Wi-Fi Sync)** | 100% offline playback of exact local files (including rare unreleased tracks) | **2 Minutes** | Plays your exact files even if a track does not exist on Spotify's public catalog. |

---

## 🚀 METHOD 1: THE EASIEST 60-SECOND WAY (CLOUD PLAYLIST TRANSFER)

We have already generated pre-categorized `.csv` and `.txt` files for every mood in `I:\\sikander-os\\data\\music\\spotify_exports\\`.

### Step-by-Step:
1. Open free web tool **[TuneMyMusic](https://www.tunemymusic.com)** (or **[Soundiiz](https://soundiiz.com)**) in your browser.
2. Click **"Let's Start"** -> Select Source: **"Upload File"** (or "From Text").
3. Choose one of the generated CSV files from `I:\\sikander-os\\data\\music\\spotify_exports\\`:
   - `01_Sunset_Deep_House.csv` ({manifest.get('01_Sunset_Deep_House', {}).get('track_count', 586)} tracks)
   - `02_Hypnotic_Trance.csv` ({manifest.get('02_Hypnotic_Trance', {}).get('track_count', 150)} tracks)
   - `03_Gym_Peak_Energy.csv` ({manifest.get('03_Gym_Peak_Energy', {}).get('track_count', 197)} tracks)
   - `04_Desi_Heritage_Sufi.csv` ({manifest.get('04_Desi_Heritage_Sufi', {}).get('track_count', 108)} tracks)
   - `05_Buddha_Bar_Lounge.csv` ({manifest.get('05_Buddha_Bar_Lounge', {}).get('track_count', 120)} tracks)
   - `06_Retro_Dance_Rock.csv` ({manifest.get('06_Retro_Dance_Rock', {}).get('track_count', 1358)} tracks)
   - *Or for your highest conviction tracks:* `00_Top_Taste_Picks_Liked.csv` ({manifest.get('00_Top_Taste_Picks_Liked', {}).get('track_count', 379)} tracks)
4. Select Destination: **"Spotify"** (log in to your Spotify account).
5. Click **"Start Transfer"**!
   - TuneMyMusic scans Spotify's 100M+ catalog, matches every track by Title and Artist, and creates the playlist directly in your Spotify library in under 60 seconds!

---

## ⚡ METHOD 2: SPOTIFY DESKTOP DIRECT PASTE (10 SECONDS)

For all tracks with verified Spotify matches, you don't even need a web importer:
1. Open the **Spotify Desktop app** on your PC.
2. Create a new playlist (e.g. `Sikander — Top Taste Picks`).
3. In `music.html`, click **"🎧 Copy URIs"** for any playlist (or open `00_Top_Taste_Picks_Liked_uris.txt` and press `Ctrl+A`, `Ctrl+C`).
4. Click inside your new Spotify playlist window and press **`Ctrl + V`**!
5. All verified tracks are instantly added to your playlist!

---

## 📁 METHOD 3: SPOTIFY NATIVE "LOCAL FILES" (100% FREE & OFFLINE)

If you want Spotify to play your exact downloaded `.mp3` files directly from your hard drive:

### Step-by-Step on PC:
1. Open the **Spotify Desktop app** on your computer.
2. Click your **Profile Picture** at the top right -> Select **Settings** (or press `Ctrl + P`).
3. Scroll down to the **"Local Files"** section.
4. Toggle ON **"Show Local Files"**.
5. Under "Show songs from", click **"Add a source"**.
6. Browse and select your `I:\\Music` folder!
7. In the left sidebar of Spotify, click **"Your Library"** -> Click the **"Local Files"** folder that just appeared.
   - Every single local song in `I:\\Music` is now directly playable in Spotify!

---

## 🎯 HOW TO PLAY BY MOOD OR PLAY ALL RANDOMLY (THE SPOTIFY FOLDER SECRET)

To seamlessly switch between:
1. Playing an exact mood (e.g. Gym or Sunset Lounge), AND
2. Playing ALL songs randomly in a master shuffle:

### Set Up the "Sikander OS Music" Playlist Folder:
1. In the **Spotify Desktop app**, right-click any empty space in your left-hand playlist sidebar.
2. Click **"Create Folder"**.
3. Name the folder: **`🎵 Sikander OS Music`**.
4. Drag your 6 mood playlists into this folder:
   - `🌅 Sunset Deep House`
   - `⚡ Gym Peak Energy`
   - `🌌 Hypnotic Trance`
   - `🪕 Desi Heritage & Sufi`
   - `☕ Buddha Bar Lounge`
   - `🎸 Retro Dance & Pop-Rock`

### How to use it:
- **To play what you're in the mood for:**  
  Click directly on that specific playlist (e.g. `⚡ Gym Peak Energy`) and hit Play.
- **To play ALL songs randomly:**  
  Click on the **Folder Name itself** (`🎵 Sikander OS Music`) and click the big green **Play** button with **Shuffle ON** (`Ctrl + S`).  
  *Spotify will automatically combine and shuffle across all 6 playlists simultaneously!*

---

## 📱 HOW TO SYNC LOCAL FILES TO YOUR PHONE (MOBILE SPOTIFY)

If you added local files on desktop and want to play them at the gym or in the car on your phone:

1. Connect your PC and Phone to the **same Wi-Fi network**.
2. On your Phone Spotify app:
   - Go to **Settings** (gear icon) -> **Local Files** -> Toggle ON **"Show audio files from this device"**.
3. On your Phone Spotify app:
   - Open any of your playlists (e.g. `⚡ Gym Peak Energy`).
   - Tap the **Download icon (green arrow / downward circle)** at the top of the playlist.
4. Spotify desktop will beam the audio files over your home Wi-Fi directly to your phone storage! Once downloaded, you can play them in airplane mode anywhere!

---

## 🛠️ EXPORTED FILES OVERVIEW IN THIS FOLDER

All files are located in `I:\\sikander-os\\data\\music\\spotify_exports\\`:

| Playlist File | Mood / Category | Format Options |
| :--- | :--- | :--- |
| `01_Sunset_Deep_House` | 🌅 Sunset Deep House | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `02_Hypnotic_Trance` | 🌌 Hypnotic Trance & Balearic | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `03_Gym_Peak_Energy` | ⚡ Gym Peak Energy | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `04_Desi_Heritage_Sufi` | 🪕 Desi Heritage & Sufi | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `05_Buddha_Bar_Lounge` | ☕ Buddha Bar & Lounge | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `06_Retro_Dance_Rock` | 🎸 Retro Dance & Pop-Rock | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `00_Top_Taste_Picks_Liked` | ⭐ Highest Conviction (90%+ & Liked) | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `00_All_Manual_Downloads` | 📁 All 1,219 Handpicked Downloads | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `00_Root_Direct_Singles` | 💾 435 Root Standalone Downloads | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |
| `00_Master_Library_All` | 🔀 Master Library ({len(tracks)} Tracks) | `.csv`, `.txt`, `_uris.txt`, `.m3u8` |

Enjoy your personalized music ecosystem!
"""

with open(guide_file, "w", encoding="utf-8") as f:
    f.write(guide_content)

print(f"Successfully generated full export package & guide in {EXPORT_DIR}")

