import os, sys, json, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"I:\sikander-os"
MUSIC_DIR = r"I:\Music"
DATA_DIR = os.path.join(ROOT, "data", "music")

with open(os.path.join(DATA_DIR, "sikander_music_library.json"), "r", encoding="utf-8") as f:
    catalog = json.load(f)

metadata = catalog.get("metadata", {})
tracks = catalog.get("tracks", [])

print(f"Total tracks in catalog: {len(tracks)}")
print("Metadata:", json.dumps(metadata, indent=2))

# 1. Check Root loose tracks
root_tracks = [t for t in tracks if t.get("is_root_manual") or t.get("source_folder") == "Root"]
print(f"Root tracks count: {len(root_tracks)}")

# Check their taste match distribution and whether any Root track has source_tier or weight lower than Tier 1
root_tiers = Counter(t.get("source_tier") for t in root_tracks)
print("Root tiers:", root_tiers)
root_matches = [t.get("taste_match") for t in root_tracks]
print(f"Root taste match min: {min(root_matches)}, max: {max(root_matches)}, avg: {sum(root_matches)/len(root_matches):.2f}")

# Check unparsed or bad artists in root
bad_artists = [t for t in root_tracks if t.get("artist") in ("Various Artists", "Unknown", "")]
print(f"Root tracks with generic artist: {len(bad_artists)}")
for b in bad_artists:
    print(f"  Generic Root: fn={b.get('raw_filename')} | title={b.get('title')}")

# 2. Check false positives in classification
print("\n--- Checking Substring Collisions in Classifiers ---")
for t in tracks:
    text = f"{t['artist']} {t['title']} {t['raw_filename']} {t.get('source_folder','')}".lower()
    for kw in ["shaan", "jal", "ott", "snr", "ltn", "francis", "marx"]:
        if kw in text and not re.search(r'\b' + re.escape(kw) + r'\b', text):
            print(f"False substring match '{kw}': artist='{t['artist']}', title='{t['title']}', cat='{t['category']}'")

# Check dedup collisions from raw files
from collections import defaultdict
import importlib.util
spec = importlib.util.spec_from_file_location("build_cat", os.path.join(DATA_DIR, "build_catalog.py"))
# We can import without re-running if we inspect raw_tracks logic
raw_files = []
for f in os.listdir(MUSIC_DIR):
    if os.path.isfile(os.path.join(MUSIC_DIR, f)) and f.lower().endswith(('.mp3', '.m4a', '.flac', '.wav')):
        raw_files.append((f, 'Root'))
for d in os.listdir(MUSIC_DIR):
    p = os.path.join(MUSIC_DIR, d)
    if os.path.isdir(p):
        for root, dirs, files in os.walk(p):
            for f in files:
                if f.lower().endswith(('.mp3', '.m4a', '.flac', '.wav')):
                    raw_files.append((f, d))

print(f"\nTotal raw files on disk: {len(raw_files)}")

# Test exact dedup logic from build_catalog with FULL normalized title
import build_catalog

groups = defaultdict(list)
for item in build_catalog.raw_tracks:
    fn = item['filename']
    folder = item['folder']
    artist, title = build_catalog.parse_track_name(fn, folder)
    norm_artist = re.sub(r'[^a-z0-9]', '', artist.lower())
    norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
    dedup_key = f"{norm_artist}_{norm_title}"
    if not norm_artist or not norm_title or norm_artist == 'variousartists':
        dedup_key = f"{norm_artist}_{re.sub(r'[^a-z0-9]', '', fn.lower())}"
    groups[dedup_key].append((fn, folder, artist, title))

print(f"\nTotal deduplicated tracks with FULL title: {len(groups)}")
actual_collisions = {k: v for k, v in groups.items() if len(v) > 1}
print(f"Duplicate groups with full title: {len(actual_collisions)}")
for k, v in actual_collisions.items():
    print(f"Key: {k} ({len(v)} tracks) -> folders: {[x[1] for x in v]}")




# 3. Check Spotify exports
export_dir = os.path.join(DATA_DIR, "spotify_exports")
if os.path.exists(export_dir):
    files = os.listdir(export_dir)
    print(f"\nSpotify exports files ({len(files)}):")
    for f in sorted(files):
        sz = os.path.getsize(os.path.join(export_dir, f))
        print(f"  {f} ({sz} bytes)")
