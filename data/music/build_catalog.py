import os, sys, json, re, hashlib, urllib.parse
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

MUSIC_DIR = r"I:\Music"
DATA_DIR = r"I:\sikander-os\data\music"
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Load Spotify data
cache_file = os.path.join(MUSIC_DIR, "spotify_cache.json")
with open(cache_file, "r", encoding="utf-8") as f:
    spotify_cache = json.load(f)

meta_cache_file = os.path.join(DATA_DIR, "spotify_metadata_cache.json")
meta_cache = {}
if os.path.exists(meta_cache_file):
    with open(meta_cache_file, "r", encoding="utf-8") as f:
        meta_cache = json.load(f)

def load_uri_list(fname):
    p = os.path.join(MUSIC_DIR, fname)
    if not os.path.exists(p):
        return set()
    with open(p, "r", encoding="utf-8") as f:
        return set(line.strip().replace("spotify:track:", "") for line in f if line.strip())

liked_set = load_uri_list("liked_uris.txt")
gym_set = load_uri_list("gym_uris.txt")
gym_fast_set = load_uri_list("gym_fast_uris.txt")
trance_set = load_uri_list("trance_uris.txt")

print(f"Loaded {len(liked_set)} liked URIs, {len(gym_set)} gym URIs, {len(trance_set)} trance URIs, {len(gym_fast_set)} gym fast URIs.")
print(f"Spotify track cache: {len(spotify_cache)} items. Metadata cache: {len(meta_cache)} items.")

# Inverted cache: match by filename variations
inv_cache = {}
for fn, sid in spotify_cache.items():
    inv_cache[fn] = sid
    inv_cache[fn.lower()] = sid
    clean_fn = re.sub(r"\[.*?\]|\(.*?\)", "", fn).strip()
    inv_cache[clean_fn.lower()] = sid

# Parsing function
def parse_track_name(filename):
    base = os.path.splitext(filename)[0]
    clean = re.sub(r"^\s*\((?:deep|edm|trance|house|mp3)\s*\)\s*", "", base, flags=re.IGNORECASE)
    clean = re.sub(r"www\.[^\s]+|http\S+|@\s*[^\s]+", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\[www\.[^\]]+\]|\(www\.[^\)]+\)", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\(1080p.*?\)|320\s*kbps|320k|128\s*kbps|HD|HQ|Official|Video|Lyrics", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"^\d+[\.\-\s_]+", "", clean)
    clean = clean.strip(" -_()[]{}")

    if not clean or len(clean) <= 1:
        clean = re.sub(r"^\d+[\.\-\s_]+", "", base).strip(" -_()[]{}")
        if not clean:
            clean = base

    artist = "Various Artists"
    title = clean

    if " - " in clean:
        pts = clean.split(" - ", 1)
        artist = pts[0].strip()
        title = pts[1].strip()
    elif "-" in clean and " " not in clean and clean.count("-") >= 2:
        pts = clean.split("-")
        artist = " ".join(pts[:2]).title()
        title = " ".join(pts[2:]).title()
    elif " by " in clean.lower():
        pts = re.split(r"\s+by\s+", clean, flags=re.IGNORECASE)
        title = pts[0].strip()
        artist = pts[1].strip()
    elif " feat " in clean.lower() or " ft " in clean.lower():
        pts = re.split(r"\s+feat\.?\s+|\s+ft\.?\s+", clean, flags=re.IGNORECASE)
        artist = pts[0].strip()
        title = "feat. " + pts[1].strip()

    artist = re.sub(r"^\d+[\.\-\s]+", "", artist).strip()
    title = re.sub(r"^\d+[\.\-\s]+", "", title).strip()

    if not title:
        title = clean or base
    if not artist:
        artist = "Various Artists"

    return artist, title

DEEP_HOUSE_ARTISTS = {
    'nora en pure', 'klingande', 'bakermat', 'ehrling', 'gostan', 'mahmut orhan', 'de hofnar',
    'vijay & sofia', 'vijay & sofia zlatko', 'sam feldt', 'kungs', 'satin jackets', 'gamper & dadoni',
    'jonas blue', 'tobtok', 'me & my toothbrush', 'anton ishutin', 'lexer', 'sonny alven', 'thomas jack',
    'scheinizzl', 'chroph', 'boehm', 'gryffin', 'flicflac', 'waze & odyssey', 'duke dumont', 'route 94',
    'alle farben', 'autograf', 'charming horses', 'filatov & karas', 'imany', 'ofenbach', 'robin schulz',
    'hugel', 'burak yeter', 'feder', 'pascal junior', 'motez', 'larse', 'supacooks', 'nikko culture',
    'housenick', 'laykkah', 'juloboy', 'deepjack', 'mr.nu', 'alex hook', 'shyam', 'alina baraz',
    'claes rosen', 'fresh produce', 'purple cocktail', 'vince forwards', 'edx', 'croatia squad', 'blood groove'
}

TRANCE_ARTISTS = {
    'chicane', 'tiesto', 'tiësto', 'armin van buuren', 'deadmau5', 'eric prydz', 'pryda', 'adam k & soha',
    'alpha 9', 'arty', 'blood groove & kikis', 'roald velden', 'lumidelic', 'dinka', 'aurosonic',
    'shingo nakamura', 'trilucid', 'reflekt', 'jan martin', 'alex h', 'lessov', 'mango', 'talamanca',
    'sunlight project', 'matt fax', 'denis neve', 'silk music', 'hazem beltagui', 'signalrunners',
    'yuri kane', 'abstract vision', 'rex mundi', 'tangerine dream', 'paul van dyk', 'atb', 'robert miles',
    '4 strings', 'daniel kandi', 'somna', 'ltn', 'biologik', 'cloudive', 'anlaya project', 'kamron schrader',
    'deepshader', 'nazca', 'fawn', 'digital sixable', 'snr', 'rikkaz', 'jan johnston', 'sound quelle',
    'technical lovers', 'tom strobe', 'headstrong', 'stine grove', 'shingo', 'aleksey', 'richard bass'
}

GYM_EDM_ARTISTS = {
    'avicii', 'calvin harris', 'david guetta', 'zedd', 'lmfao', 'don omar', 'daddy yankee', 'pitbull',
    'benny benassi', 'fedde le grand', 'fatboy slim', 'afrojack', 'swedish house mafia', 'hardwell',
    'skrillex', 'showtek', 'oliver $', 'dubdogz', '50 cent', 'kid cudi', 'major lazer', 'dj snake',
    'far east movement', 'will.i.am', 'the white stripes', 'kaskade', 'manufactured superstars',
    'marx', 'stephan f', 'vitas', 'caravan palace', 'francis', 'fabricio pecanha', 'naxsy', 'remady',
    'manu l', 'touch and go', 'pierce fulton', 'shoffy', 'lincoln jesser', 'twenty one pilots', 'uppermost'
}

DESI_ARTISTS = {
    'nusrat fateh ali khan', 'nfak', 'rahat fateh ali khan', 'fuzon', 'junoon', 'atif aslam', 'ali azmat',
    'strings', 'e.p.', 'entity paradigm', 'kailash kher', 'lucky ali', 'euphoria', 'palash sen',
    'a.r. rahman', 'ar rahman', 'mohit chauhan', 'roopkumar rathod', 'ahmed jahanzeb', 'bally sagoo',
    'bombay vikings', 'sonu nigam', 'pankaj udhas', 'shaan', 'hadiqa kiani', 'ali zafar', 'karavan',
    'ali haidar', 'aryans', 'shiamak davar', 'jal', 'vital signs', 'junaid jamshed', 'sajjad ali',
    'najam sheraz', 'faakhir', 'haroon', 'jawad ahmad', 'bilal saeed', 'imran khan', 'jazzy b',
    'daler mehndi', 'amar arshi', 'badshah', 'neha kakkar', 'arijit singh', 'jubin nautiyal',
    'palak muchhal', 'shashaa tirupati', 'arif lohar', 'harshdeep kaur', 'abida parveen'
}

LOUNGE_ARTISTS = {
    'buddha bar', 'buddha-bar', 'blank & jones', 'schiller', 'lemongrass', 'moby', 'karunesh', 'yiruma',
    'deep forest', 'dido', 'the xx', 'claude challe', 'ravin', 'david visan', 'bliss', 'my phuong nguyen',
    'thierry david', 'al-pha-x', 'afterlife', 'ryukyu underground', 'supervielle', 'ustad sultan khan',
    'ravi prasad', 'phatjak', 'solitude', 'ott', 'deepak chopra', 'halimag'
}

def classify_track(artist, title, filename, folder, is_in_trance, is_in_gym, is_in_liked):
    text = f"{artist} {title} {filename} {folder}".lower()
    
    if folder == "Desi" or any(a in text for a in DESI_ARTISTS):
        category = "Desi Heritage & Sufi"
        mood = "Desi Soul & Sufi"
        energy = "Medium-High"
        bpm = "85-115 BPM"
        pillar = "Pillar 4: Soulful Desi Heritage & Melodic Sufi / Pop (Weight: 15%)"
        reason = "Deep South Asian vocal acoustics, emotive poetry, and cultural nostalgic soul."
        return category, mood, energy, bpm, pillar, reason

    if is_in_trance or "search of sunrise" in text or "elements of life" in text or any(a in text for a in TRANCE_ARTISTS):
        category = "Hypnotic Trance & Balearic"
        mood = "Hypnotic Trance"
        energy = "High"
        bpm = "128-136 BPM"
        pillar = "Pillar 2: Hypnotic Progressive Trance & Sunset Balearic (Weight: 20%)"
        reason = "Expansive progressive synth arpeggios, ethereal breakdowns, and late-night flow state."
        return category, mood, energy, bpm, pillar, reason

    if is_in_gym or any(a in text for a in GYM_EDM_ARTISTS) or "gym" in text:
        category = "Gym Peak Energy"
        mood = "Gym / High Energy"
        energy = "Peak / Explosive"
        bpm = "126-132 BPM"
        pillar = "Pillar 3: High-Energy Gym & Peak Electronic Drive (Weight: 20%)"
        reason = "Driving 4-on-the-floor kick, motivating electronic builds, and PR progressive overload fuel."
        return category, mood, energy, bpm, pillar, reason

    if "sax" in text or "deep" in folder.lower() or "ehrling" in text or any(a in text for a in DEEP_HOUSE_ARTISTS):
        category = "Sunset Deep House"
        mood = "Sunset Deep House"
        energy = "Medium-High"
        bpm = "120-124 BPM"
        pillar = "Pillar 1: Sunset Deep House & Saxophone Melodic Chill (Weight: 25%)"
        reason = "Warm rolling bassline, organic saxophone/piano hooks, and euphoric sunset dopamine."
        return category, mood, energy, bpm, pillar, reason

    if "buddha" in text or "relax" in text or "nomads" in text or any(a in text for a in LOUNGE_ARTISTS):
        category = "Buddha Bar Lounge"
        mood = "Buddha Bar Lounge"
        energy = "Mellow / Ambient"
        bpm = "80-105 BPM"
        pillar = "Pillar 5: Atmospheric Lounge, Buddha Bar & World Chillout (Weight: 10%)"
        reason = "Serene downtempo world groove, ethnic acoustic strings, and evening contemplative zen."
        return category, mood, energy, bpm, pillar, reason

    category = "Retro Dance & Pop-Rock"
    mood = "Retro Dance & Pop-Rock"
    energy = "Medium-High"
    bpm = "112-128 BPM"
    pillar = "Pillar 6: 90s-2000s Nostalgic Dance-Pop & Melodic Alt-Rock (Weight: 10%)"
    reason = "Timeless hook, nostalgic millennial melody, and feel-good singalong energy."
    return category, mood, energy, bpm, pillar, reason

def calculate_taste_match(source_tier, is_ym, is_desi, is_liked, is_gym, is_trance, category, has_spotify):
    score = 75
    if is_ym:
        score += 12
    elif is_desi:
        score += 12
    elif "Tier 1" in source_tier:
        score += 10
    else:
        score += 6

    if is_liked:
        score += 5
    if is_trance or is_gym:
        score += 4
    if has_spotify:
        score += 2

    if category == "Sunset Deep House":
        score += 3
    elif category == "Hypnotic Trance & Balearic":
        score += 2
    elif category == "Gym Peak Energy":
        score += 2
    elif category == "Desi Heritage & Sufi":
        score += 2

    return min(99, max(75, score))

# Scan all audio files
raw_tracks = []

root_files = [f for f in os.listdir(MUSIC_DIR) if os.path.isfile(os.path.join(MUSIC_DIR, f)) and f.lower().endswith(('.mp3', '.m4a', '.flac', '.wav'))]
for f in root_files:
    raw_tracks.append({
        'filename': f,
        'folder': 'Root',
        'is_ym': False,
        'is_desi': False,
        'source_tier': 'Tier 1: Manual Curated (Root)'
    })

for d in os.listdir(MUSIC_DIR):
    p = os.path.join(MUSIC_DIR, d)
    if not os.path.isdir(p):
        continue
    parts = d.split(' ')
    is_ym = len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 4
    is_desi = (d.lower() == 'desi')

    if is_ym:
        tier = f'Tier 1: Manual Curated ({d})'
    elif is_desi:
        tier = 'Tier 1: Desi Heritage & Sufi (Hand-Selected)'
    else:
        tier = f'Tier 2: Collection Archive ({d})'

    for root, dirs, files in os.walk(p):
        for f in files:
            if f.lower().endswith(('.mp3', '.m4a', '.flac', '.wav')):
                raw_tracks.append({
                    'filename': f,
                    'folder': d,
                    'is_ym': is_ym,
                    'is_desi': is_desi,
                    'source_tier': tier
                })

print(f"Total raw tracks scanned: {len(raw_tracks)}")

CATEGORY_THUMBS = {
    'Sunset Deep House': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500&auto=format&fit=crop&q=80',
    'Hypnotic Trance & Balearic': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80',
    'Gym Peak Energy': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&auto=format&fit=crop&q=80',
    'Desi Heritage & Sufi': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=500&auto=format&fit=crop&q=80',
    'Buddha Bar Lounge': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80',
    'Retro Dance & Pop-Rock': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500&auto=format&fit=crop&q=80'
}

tracks_by_key = {}

for item in raw_tracks:
    fn = item['filename']
    folder = item['folder']
    is_ym = item['is_ym']
    is_desi = item['is_desi']
    source_tier = item['source_tier']

    spotify_id = inv_cache.get(fn) or inv_cache.get(fn.lower())
    if not spotify_id:
        clean_fn = re.sub(r'\[.*?\]|\(.*?\)', '', fn).strip()
        spotify_id = inv_cache.get(clean_fn.lower())

    meta = meta_cache.get(spotify_id) if spotify_id else None

    is_liked = spotify_id in liked_set if spotify_id else False
    is_gym = (spotify_id in gym_set or spotify_id in gym_fast_set) if spotify_id else False
    is_trance = spotify_id in trance_set if spotify_id else False
    is_gym_fast = spotify_id in gym_fast_set if spotify_id else False

    if meta and meta.get('title'):
        full_title = meta['title']
        if ' - ' in full_title:
            artist, title = full_title.split(' - ', 1)
        elif ' by ' in full_title.lower():
            title, artist = re.split(r'\s+by\s+', full_title, flags=re.IGNORECASE)
        else:
            artist, title = parse_track_name(fn)
            title = full_title
    else:
        artist, title = parse_track_name(fn)

    artist = re.sub(r'\s+', ' ', artist).strip()
    title = re.sub(r'\s+', ' ', title).strip()

    category, mood, energy, bpm, pillar, reason = classify_track(
        artist, title, fn, folder, is_trance, is_gym, is_liked
    )

    taste_match = calculate_taste_match(source_tier, is_ym, is_desi, is_liked, is_gym, is_trance, category, bool(spotify_id))

    norm_artist = re.sub(r'[^a-z0-9]', '', artist.lower())
    norm_title = re.sub(r'[^a-z0-9]', '', title.lower()[:25])
    dedup_key = f"{norm_artist}_{norm_title}"
    if not norm_artist or not norm_title:
        dedup_key = fn.lower()

    thumb = None
    if meta and meta.get('thumbnail_url'):
        thumb = meta['thumbnail_url']
    else:
        thumb = CATEGORY_THUMBS.get(category, CATEGORY_THUMBS['Sunset Deep House'])

    track_obj = {
        'id': f"track_{hashlib.md5(dedup_key.encode()).hexdigest()[:10]}",
        'title': title,
        'artist': artist,
        'raw_filename': fn,
        'source_folder': folder,
        'source_tier': source_tier,
        'is_manual_download': is_ym or is_desi or (folder == 'Root'),
        'is_ym': is_ym,
        'is_desi': is_desi,
        'category': category,
        'mood': mood,
        'energy': energy,
        'bpm_range': bpm,
        'taste_match': taste_match,
        'taste_pillar': pillar,
        'taste_reason': reason,
        'spotify_id': spotify_id,
        'spotify_uri': f"spotify:track:{spotify_id}" if spotify_id else None,
        'spotify_url': f"https://open.spotify.com/track/{spotify_id}" if spotify_id else None,
        'thumbnail_url': thumb,
        'in_spotify_liked': is_liked,
        'in_spotify_gym': is_gym,
        'in_spotify_trance': is_trance,
        'in_spotify_gym_fast': is_gym_fast,
        'youtube_search_url': f"https://www.youtube.com/results?search_query={urllib.parse.quote(f'{artist} {title}')}",
        'spotify_search_url': f"https://open.spotify.com/search/{urllib.parse.quote(f'{artist} {title}')}"
    }

    if dedup_key not in tracks_by_key:
        tracks_by_key[dedup_key] = track_obj
    else:
        existing = tracks_by_key[dedup_key]
        if track_obj['is_manual_download'] and not existing['is_manual_download']:
            tracks_by_key[dedup_key] = track_obj
        if is_ym:
            existing['is_ym'] = True
        if is_desi:
            existing['is_desi'] = True
        if track_obj['in_spotify_liked']:
            existing['in_spotify_liked'] = True
        if track_obj['in_spotify_gym']:
            existing['in_spotify_gym'] = True
        if track_obj['in_spotify_trance']:
            existing['in_spotify_trance'] = True
        if track_obj['in_spotify_gym_fast']:
            existing['in_spotify_gym_fast'] = True
        if track_obj['spotify_id'] and not existing['spotify_id']:
            existing['spotify_id'] = track_obj['spotify_id']
            existing['spotify_uri'] = track_obj['spotify_uri']
            existing['spotify_url'] = track_obj['spotify_url']
            existing['thumbnail_url'] = track_obj['thumbnail_url']
        existing['taste_match'] = max(existing['taste_match'], track_obj['taste_match'])

unified_tracks = list(tracks_by_key.values())
unified_tracks.sort(key=lambda t: (-t['taste_match'], t['artist'].lower(), t['title'].lower()))

category_counts = Counter(t['category'] for t in unified_tracks)
mood_counts = Counter(t['mood'] for t in unified_tracks)
ym_count = sum(1 for t in unified_tracks if t.get('is_ym'))
desi_count = sum(1 for t in unified_tracks if t.get('is_desi'))
manual_count = sum(1 for t in unified_tracks if t['is_manual_download'])
spotify_matched_count = sum(1 for t in unified_tracks if t['spotify_id'])
liked_count = sum(1 for t in unified_tracks if t['in_spotify_liked'])
gym_count = sum(1 for t in unified_tracks if t['in_spotify_gym'])
trance_count = sum(1 for t in unified_tracks if t['in_spotify_trance'])

database_payload = {
    'metadata': {
        'catalog_name': "Sikander's Master Music Intelligence & Taste Catalog",
        'generated_at': "2026-09-13T01:00:00+05:00",
        'total_tracks': len(unified_tracks),
        'manual_downloads_count': ym_count,
        'total_manual_picks': manual_count,
        'desi_tracks_count': desi_count,
        'spotify_matched_count': spotify_matched_count,
        'spotify_liked_count': liked_count,
        'spotify_gym_count': gym_count,
        'spotify_trance_count': trance_count,
        'categories': dict(category_counts),
        'moods': dict(mood_counts),
        'taste_pillars': [
            {'id': 'pillar_1', 'name': 'Sunset Deep House & Saxophone Melodic Chill', 'weight': 25, 'target_bpm': '118-124 BPM'},
            {'id': 'pillar_2', 'name': 'Hypnotic Progressive Trance & Sunset Balearic', 'weight': 20, 'target_bpm': '128-136 BPM'},
            {'id': 'pillar_3', 'name': 'High-Energy Gym & Peak Electronic Drive', 'weight': 20, 'target_bpm': '126-132 BPM'},
            {'id': 'pillar_4', 'name': 'Soulful Desi Heritage & Melodic Sufi / Pop', 'weight': 15, 'target_bpm': '85-115 BPM'},
            {'id': 'pillar_5', 'name': 'Atmospheric Lounge, Buddha Bar & World Chillout', 'weight': 10, 'target_bpm': '80-105 BPM'},
            {'id': 'pillar_6', 'name': '90s-2000s Nostalgic Dance-Pop & Melodic Alt-Rock', 'weight': 10, 'target_bpm': '112-128 BPM'}
        ]
    },
    'tracks': unified_tracks
}

out_file = os.path.join(DATA_DIR, "sikander_music_library.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(database_payload, f, indent=2, ensure_ascii=False)

js_file = os.path.join(DATA_DIR, "sikander_music_library.js")
with open(js_file, "w", encoding="utf-8") as f:
    f.write("window.SIKANDER_MUSIC_DATA = ")
    json.dump(database_payload, f, ensure_ascii=False)
    f.write(";\n")

print(f"Successfully wrote master database to {out_file} ({os.path.getsize(out_file)} bytes)")
print(f"Successfully wrote standalone JS database to {js_file} ({os.path.getsize(js_file)} bytes)")
print(f"Total deduplicated tracks: {len(unified_tracks)}")
print(f"Manual Year-Month tracks: {ym_count}, Desi tracks: {desi_count}, Total manual archive picks: {manual_count}")
print("Category distribution:", dict(category_counts))
print("Mood distribution:", dict(mood_counts))
