import os, sys, json, re, hashlib, urllib.parse
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

MUSIC_DIR = r"I:\Music"
DATA_DIR = r"I:\sikander-os\data\music"
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Load Spotify data and URIs
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

# Known album tracks in Root
COLDPLAY_ROOT = {
    '03. don\'t panic': ('Coldplay', 'Don\'t Panic'),
    'don\'t panic': ('Coldplay', 'Don\'t Panic'),
    '04. speed of sound': ('Coldplay', 'Speed Of Sound'),
    'speed of sound': ('Coldplay', 'Speed Of Sound'),
    '05. violet hill': ('Coldplay', 'Violet Hill'),
    'violet hill': ('Coldplay', 'Violet Hill'),
    '06. every teardrop is a waterfall': ('Coldplay', 'Every Teardrop Is A Waterfall'),
    'every teardrop is a waterfall': ('Coldplay', 'Every Teardrop Is A Waterfall'),
    '08. trouble': ('Coldplay', 'Trouble'),
    'trouble': ('Coldplay', 'Trouble'),
    '10. yellow': ('Coldplay', 'Yellow'),
    'yellow': ('Coldplay', 'Yellow'),
    '11. in my place': ('Coldplay', 'In My Place'),
    'in my place': ('Coldplay', 'In My Place'),
    '12. god put a smile upon your face': ('Coldplay', 'God Put A Smile Upon Your Face'),
    'god put a smile upon your face': ('Coldplay', 'God Put A Smile Upon Your Face'),
    '14. talk': ('Coldplay', 'Talk'),
    'talk': ('Coldplay', 'Talk'),
    '15. shiver': ('Coldplay', 'Shiver'),
    'shiver': ('Coldplay', 'Shiver'),
    '16. the hardest part': ('Coldplay', 'The Hardest Part'),
    'the hardest part': ('Coldplay', 'The Hardest Part'),
    '18. fix you': ('Coldplay', 'Fix You'),
    'fix you': ('Coldplay', 'Fix You')
}

SAVAGE_GARDEN_ROOT = {
    '01 - i want you': ('Savage Garden', 'I Want You'),
    'i want you': ('Savage Garden', 'I Want You'),
    '02 - i knew i loved you': ('Savage Garden', 'I Knew I Loved You'),
    'i knew i loved you': ('Savage Garden', 'I Knew I Loved You'),
    '08 - truly madly deeply': ('Savage Garden', 'Truly Madly Deeply'),
    'truly madly deeply': ('Savage Garden', 'Truly Madly Deeply')
}

KNOWN_ROOT_TRACKS = {
    '01 addicted to love \'97': ('Robert Palmer', 'Addicted to Love \'97'),
    '01 cups (pitch perfect_s _when i_m gone_)': ('Anna Kendrick', 'Cups (When I\'m Gone)'),
    '01-san-francisco-be-sure-to-wear-flowers-in-your-hair': ('Scott McKenzie', 'San Francisco (Be Sure to Wear Flowers in Your Hair)'),
    '04 - al-pha-x- an indian summer': ('Al-Pha-X', 'An Indian Summer'),
    '07 - indian gipsy (ravi prasad)': ('Ravi Prasad', 'Indian Gipsy'),
    '09 - phatjak vs- dj hamoodi - ritmo caliente': ('Phatjak vs DJ Hamoodi', 'Ritmo Caliente'),
    '1\'st lady - i think im falling in love': ('1st Lady', 'I Think I\'m Falling In Love'),
    '10': ('Various Artists', 'Track 10'),
    '13 - inna - endless': ('INNA', 'Endless'),
    '15 - schiller - i feel you': ('Schiller', 'I Feel You'),
    'eye of the tiger -lyrics-': ('Survivor', 'Eye of the Tiger'),
    'eye of the tiger': ('Survivor', 'Eye of the Tiger'),
    'hey there delilah lyrics..': ('Plain White T\'s', 'Hey There Delilah'),
    'hey there delilah lyrics.': ('Plain White T\'s', 'Hey There Delilah'),
    'hey there delilah lyrics': ('Plain White T\'s', 'Hey There Delilah'),
    'hey there delilah': ('Plain White T\'s', 'Hey There Delilah'),
    'bleed it out': ('Linkin Park', 'Bleed It Out'),
    'chocolate': ('Snow Patrol', 'Chocolate'),
    'in the navy!!': ('Village People', 'In The Navy'),
    'jennifer paige crush': ('Jennifer Paige', 'Crush'),
    'cupid\'s chokehold [lyrics]': ('Gym Class Heroes', 'Cupid\'s Chokehold'),
    'don t wanna miss a thing aerosmith mp3 download': ('Aerosmith', 'I Don\'t Want to Miss a Thing'),
    'spectrum zedd mp3 download': ('Zedd ft. Matthew Koma', 'Spectrum'),
    'trance - 009 sound system dreamscape': ('009 Sound System', 'Dreamscape'),
    'a1 same old brand new you': ('A1', 'Same Old Brand New You'),
    'another chance hed kandi': ('Roger Sanchez', 'Another Chance'),
    'bones lewis watson mp3 downloads _ www.myfreemp3.us': ('Lewis Watson', 'Bones'),
    'bora bora music house ibiza (song of trumpetman)': ('DJ Pippi & Jamie Lewis', 'Song of Trumpetman (Ibiza Chill)'),
    'break the rules charli xcx xcx mp3 download': ('Charli XCX', 'Break The Rules'),
    'code geass soundtrack stories': ('Hitomi Kuroishi', 'Stories'),
    'deep inside': ('Harddrive / Mary J. Blige', 'Deep Inside'),
    'erotic city megamix': ('Prince / Various', 'Erotic City Megamix'),
    'find you_\'re here _ find you_\'re gone': ('Kirsty Hawkshaw vs. Tiësto', 'Just Be / Find You\'re Gone'),
    'forever young jay-z lyrics': ('JAY-Z ft. Mr Hudson', 'Young Forever'),
    'ftv winter chill_ come baby': ('Fashion TV Lounge', 'Winter Chill (Come Baby)'),
    'halimag  kalmyk dance (16)': ('Halimag', 'Kalmyk Dance'),
    'hot summer night oh la la la david tavare featuring elvissa': ('David Tavaré ft. 2 Eivissa', 'Hot Summer Night (Oh La La La)'),
    'if you had my love [pablo flores remix] full lenght': ('Jennifer Lopez', 'If You Had My Love (Pablo Flores Remix)'),
    'lalala techno dance': ('Various Artists', 'LaLaLa Techno Dance'),
    'liongold   garden of the world (true love remix).mov': ('Liongold', 'Garden Of The World (True Love Remix)'),
    'liongold nitefly mp3 download _ myfreemp3.eu': ('Liongold', 'Nitefly'),
    'living it all ftv &quot;beach life essentials&quot;': ('Fashion TV Lounge', 'Living It All (Beach Life Essentials)'),
    'make the girl dance \'baby baby baby\'': ('Make The Girl Dance', 'Baby Baby Baby'),
    'melodic progressive house mix vol 14 (on the road)_2': ('Silk Music / Various', 'Melodic Progressive House Mix Vol 14 (On The Road)'),
    'melodic progressive house mix vol 15 (perfect life)': ('Silk Music / Various', 'Melodic Progressive House Mix Vol 15 (Perfect Life)'),
    'melodic progressive house mix vol 24 (city lights)': ('Silk Music / Various', 'Melodic Progressive House Mix Vol 24 (City Lights)'),
    'milky just the way you are': ('Milky', 'Just The Way You Are'),
    'nari nari': ('Hisham Abbas', 'Nari Narain (Habibi Dah)'),
    'no mercy where do you go lyrics': ('No Mercy', 'Where Do You Go'),
    'numa numa action!': ('O-Zone', 'Dragostea Din Tei (Numa Numa)'),
    'pure garage (im sorry)': ('Pure Garage / Various', 'I\'m Sorry'),
    'requiem for a dream remix (paul oakenfold)': ('Paul Oakenfold', 'Requiem for a Dream (Remix)'),
    'reverend and the makers the state of things (great quality)': ('Reverend and the Makers', 'The State of Things'),
    'shalala vengaboys lycris': ('Vengaboys', 'Shalala Lala'),
    'shania twain that don\'t impress me much (lyrics in description)': ('Shania Twain', 'That Don\'t Impress Me Much'),
    'she was your everything': ('Aviation', 'She Was Your Everything'),
    'son of man': ('Phil Collins', 'Son of Man'),
    'stay see summer mix 15': ('Stay See', 'Summer Mix 15 (Melodic Deep House)'),
    'swamp thing  ( the grid)': ('The Grid', 'Swamp Thing'),
    'timber mp3 download': ('Pitbull ft. Ke$ha', 'Timber'),
    'tortured soul &quot;always in heaven when i\'m with you&quot; at java jazz festival 2006': ('Tortured Soul', 'Always In Heaven When I\'m With You'),
    'tortured soul love mp3 download': ('Tortured Soul', 'Fall In Love'),
    'toura toura remix': ('Cheb Mami', 'Toura Toura (Remix)'),
    'what does the fox say mp3 download_2': ('Ylvis', 'The Fox (What Does The Fox Say?)'),
    'why \'d i have to fall in love with you- dimension-x_2': ('Dimension-X', 'Why\'d I Have To Fall In Love With You'),
    'will smith miami lyrics': ('Will Smith', 'Miami'),
    'you + me   ftv beach life essentials': ('Fashion TV Lounge', 'You + Me (Beach Life Essentials)'),
    'you were my everything': ('Aviation', 'You Were My Everything'),
    'big mistake': ('Natalie Imbruglia', 'Big Mistake'),
    'sanctuary song': ('Utada Hikaru', 'Sanctuary'),
    'orac_randomprophecies_10': ('Orac', 'Random Prophecies (Part 10)'),
    'orac randomprophecies 10': ('Orac', 'Random Prophecies (Part 10)'),
    'best dance music #1': ('Various Artists', 'Best Dance Music #1'),
    'tune': ('Various Artists', 'Tune'),
    'play_2': ('Various Artists', 'Play (Part 2)'),
    'play 2': ('Various Artists', 'Play (Part 2)'),
    'play_3': ('Various Artists', 'Play (Part 3)'),
    'play 3': ('Various Artists', 'Play (Part 3)'),
    'play_4': ('Various Artists', 'Play (Part 4)'),
    'play 4': ('Various Artists', 'Play (Part 4)'),
    'play_5': ('Various Artists', 'Play (Part 5)'),
    'play 5': ('Various Artists', 'Play (Part 5)')
}

def clean_text(s):
    if not s: return ''
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\(\s*\)|\[\s*\]|\{\s*\}', '', s)
    s = s.strip(' -_~:;,.\'\"')
    if s.count('(') > s.count(')'):
        s = s + ')'
    elif s.count('[') > s.count(']'):
        s = s + ']'
    return s.strip(' -_~:;,.\'\"')

def get_folder_artist(folder):
    if not folder or folder in ['Root', 'Desi', 'Songs', 'Fire', 'Indie', 'Discoteca Anni 90', 'Progressive techno', 'Switzerland', 'Basic Instinct', 'Believe', 'Away from the Sun', 'Busted Stuff', 'Best Of House 16']:
        return None
    parts = folder.split(' ')
    if len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 4:
        return None
    if folder.startswith('(') and any(y in folder for y in ['2001', '2007', '2012', '2013', '2014']):
        return None
    if any(comp in folder.lower() for comp in ['beatport', 'hed kandi', 'top 100', 'top 20', 'deep 2019', 'sax house', 'buddha bar', 'buddha-bar', 'relax cd', 'va -', 'various']):
        return None
    
    fl = folder.lower()
    if 'ehrling' in fl: return 'Ehrling'
    if 'coldplay' in fl: return 'Coldplay'
    if 'daft punk' in fl: return 'Daft Punk'
    if 'calvin harris' in fl: return 'Calvin Harris'
    if 'linken park' in fl or 'linkin park' in fl: return 'Linkin Park'
    if 'nirvana' in fl: return 'Nirvana'
    if 'bruce springsteen' in fl: return 'Bruce Springsteen'
    if 'maroon 5' in fl: return 'Maroon 5'
    if 'vengaboys' in fl: return 'Vengaboys'
    if 'lisa shaw' in fl: return 'Lisa Shaw'
    if 'fatboy slim' in fl: return 'Fatboy Slim'
    if 'the cranberries' in fl: return 'The Cranberries'
    if 'allen jackson' in fl or 'alan jackson' in fl: return 'Alan Jackson'
    if 'avril lavigne' in fl: return 'Avril Lavigne'
    if 'justin timberlake' in fl: return 'Justin Timberlake'
    if 'sting' in fl: return 'Sting'
    if 'yiruma' in fl: return 'Yiruma'
    if 'the script' in fl: return 'The Script'
    if 'the kooks' in fl: return 'The Kooks'
    if 'miguel migs' in fl: return 'Miguel Migs'
    if fl == 'iio': return 'iiO'
    if 'akcent' in fl: return 'Akcent'
    if 'cheryl cole' in fl: return 'Cheryl Cole'
    if 'eagle eye cherry' in fl: return 'Eagle-Eye Cherry'
    if 'fort minor' in fl: return 'Fort Minor'
    if 'haddaway' in fl: return 'Haddaway'
    if 'ian pooley' in fl: return 'Ian Pooley'
    if 'lostprophets' in fl: return 'Lostprophets'
    if 'neil young' in fl: return 'Neil Young'
    if 'mark knopfler' in fl: return 'Mark Knopfler'
    if 'dave matthews band' in fl: return 'Dave Matthews Band'
    if 'chemical brothers' in fl: return 'The Chemical Brothers'

    if ' - ' in folder:
        return clean_text(folder.split(' - ')[0])
    m = re.match(r'^([^\[\{\(]+)', folder)
    if m:
        art = clean_text(m.group(1))
        if art and len(art) > 2:
            return art
    return clean_text(folder)

ALL_KNOWN_ARTISTS = [
    ('bruce springsteen', 'Bruce Springsteen'),
    ('calvin harris', 'Calvin Harris'),
    ('gregory and the hawk', 'Gregory and the Hawk'),
    ('gorillaz', 'Gorillaz'),
    ('gorrilaz', 'Gorillaz'),
    ('charli xcx', 'Charli XCX'),
    ('taylor swift', 'Taylor Swift'),
    ('entity paradigm', 'Entity Paradigm (E.P.)'),
    ('e.p.', 'Entity Paradigm (E.P.)'),
    ('bally sagoo', 'Bally Sagoo'),
    ('karavan', 'Karavan'),
    ('lewis watson', 'Lewis Watson'),
    ('plain white t\'s', 'Plain White T\'s'),
    ('aerosmith', 'Aerosmith'),
    ('snow patrol', 'Snow Patrol'),
    ('linkin park', 'Linkin Park'),
    ('trapt', 'Trapt'),
    ('nickelback', 'Nickelback'),
    ('survivor', 'Survivor'),
    ('atc', 'ATC'),
    ('david guetta', 'David Guetta'),
    ('avicii', 'Avicii'),
    ('deadmau5', 'Deadmau5'),
    ('eric prydz', 'Eric Prydz'),
    ('chicane', 'Chicane'),
    ('armin van buuren', 'Armin van Buuren'),
    ('nora en pure', 'Nora En Pure'),
    ('klingande', 'Klingande'),
    ('mahmut orhan', 'Mahmut Orhan'),
    ('bakermat', 'Bakermat'),
    ('fatboy slim', 'Fatboy Slim'),
    ('moby', 'Moby'),
    ('schiller', 'Schiller'),
    ('blank & jones', 'Blank & Jones'),
    ('blank and jones', 'Blank & Jones'),
    ('yiruma', 'Yiruma'),
    ('karunesh', 'Karunesh'),
    ('nusrat fateh ali khan', 'Nusrat Fateh Ali Khan'),
    ('nfak', 'Nusrat Fateh Ali Khan'),
    ('atif aslam', 'Atif Aslam'),
    ('fuzon', 'Fuzon'),
    ('junoon', 'Junoon'),
    ('kailash kher', 'Kailash Kher'),
    ('lucky ali', 'Lucky Ali'),
    ('strings', 'Strings'),
    ('ahmed jahanzeb', 'Ahmed Jahanzeb'),
    ('bombay vikings', 'Bombay Vikings'),
    ('sonu nigam', 'Sonu Nigam'),
    ('pankaj udhas', 'Pankaj Udhas'),
    ('ali azmat', 'Ali Azmat'),
    ('daler mehndi', 'Daler Mehndi'),
    ('badshah', 'Badshah'),
    ('arijit singh', 'Arijit Singh'),
    ('jubin nautiyal', 'Jubin Nautiyal'),
    ('palak muchhal', 'Palak Muchhal'),
    ('shashaa tirupati', 'Shashaa Tirupati'),
    ('blood groove & kikis', 'Blood Groove & Kikis'),
    ('blood groove', 'Blood Groove & Kikis'),
    ('alpha 9', 'Alpha 9'),
    ('roald velden', 'Roald Velden'),
    ('lumidelic', 'Lumidelic'),
    ('aurosonic', 'Aurosonic'),
    ('shingo nakamura', 'Shingo Nakamura'),
    ('trilucid', 'Trilucid'),
    ('reflekt', 'Reflekt'),
    ('vijay & sofia', 'Vijay & Sofia'),
    ('vijay & sofia zlatko', 'Vijay & Sofia'),
    ('de hofnar', 'De Hofnar'),
    ('gostan', 'Gostan'),
    ('satin jackets', 'Satin Jackets'),
    ('gamper & dadoni', 'Gamper & Dadoni'),
    ('tobtok', 'Tobtok'),
    ('me & my toothbrush', 'Me & My Toothbrush'),
    ('pascal junior', 'Pascal Junior'),
    ('charming horses', 'Charming Horses'),
    ('filatov & karas', 'Filatov & Karas'),
    ('robin schulz', 'Robin Schulz'),
    ('coldplay', 'Coldplay'),
    ('the script', 'The Script'),
    ('nirvana', 'Nirvana'),
    ('the cranberries', 'The Cranberries'),
    ('modjo', 'Modjo'),
    ('sash!', 'Sash!'),
    ('sash', 'Sash!'),
    ('vengaboys', 'Vengaboys'),
    ('edward maya', 'Edward Maya'),
    ('inna', 'INNA'),
    ('akcent', 'Akcent'),
    ('kylie minogue', 'Kylie Minogue'),
    ('maroon 5', 'Maroon 5'),
    ('matchbox twenty', 'Matchbox Twenty'),
    ('don omar', 'Don Omar'),
    ('daddy yankee', 'Daddy Yankee'),
    ('pitbull', 'Pitbull'),
    ('zedd', 'Zedd'),
    ('lmfao', 'LMFAO'),
    ('benny benassi', 'Benny Benassi'),
    ('fedde le grand', 'Fedde Le Grand'),
    ('swedish house mafia', 'Swedish House Mafia'),
    ('50 cent', '50 Cent'),
    ('kid cudi', 'Kid Cudi'),
    ('the white stripes', 'The White Stripes'),
    ('kaskade', 'Kaskade'),
    ('tiesto', 'Tiësto'),
    ('tiësto', 'Tiësto'),
    ('adam k & soha', 'Adam K & Soha'),
    ('adam k and soha', 'Adam K & Soha'),
    ('arty', 'Arty'),
    ('dinka', 'Dinka'),
    ('jan martin', 'Jan Martin'),
    ('alex h', 'Alex H'),
    ('mango', 'Mango'),
    ('talamanca', 'Talamanca'),
    ('sunlight project', 'Sunlight Project'),
    ('robert miles', 'Robert Miles'),
    ('4 strings', '4 Strings'),
    ('atb', 'ATB'),
    ('buddha bar', 'Buddha-Bar'),
    ('buddha-bar', 'Buddha-Bar'),
    ('lemongrass', 'Lemongrass'),
    ('dido', 'Dido'),
    ('the xx', 'The XX')
]

def parse_track_name(filename, folder='Root'):
    base = os.path.splitext(filename)[0]
    base_lower = base.lower().strip()
    base_clean = re.sub(r'[._\s]+', ' ', base_lower).strip()

    if folder == 'Root':
        for k, v in COLDPLAY_ROOT.items():
            if base_lower == k or base_clean == k or base_lower.strip(' .-_') == k: return v[0], v[1]
        for k, v in SAVAGE_GARDEN_ROOT.items():
            if base_lower == k or base_clean == k or base_lower.strip(' .-_') == k: return v[0], v[1]
        for k, v in KNOWN_ROOT_TRACKS.items():
            if base_lower == k or base_clean == k or base_lower.strip(' .-_') == k: return v[0], v[1]

    # Check for Ott chillout prefix
    if base_lower.startswith(('ott-', 'ott -', 'ott_')):
        art = "Ott"
        tit = re.sub(r'^ott[\s\-_]+', '', base, flags=re.IGNORECASE)
        return clean_text(art), clean_text(tit)

    # Handle Desi naming like: (Song) - Tu Jo Nahi To - {Ahmed Jahanzeb}
    if folder == 'Desi' or '{' in base:
        m = re.search(r'\{([^}]+)\}', base)
        if m:
            art = m.group(1).strip()
            tit = re.sub(r'\(Song\)\s*[-:]?\s*|\{[^}]+\}', '', base, flags=re.IGNORECASE).strip(' -_')
            if art and tit:
                return clean_text(art), clean_text(tit)

    clean = base
    clean = re.sub(r'^\[(?:-320|\+320)\]™?\s*', '', clean)
    clean = re.sub(r'^#\w+▶\w+®?\s*-\s*', '', clean)
    clean = re.sub(r'^Telegram-\s*@\w+\s*-\s*', '', clean)
    clean = re.sub(r'^\s*\(deep|edm|trance|house|mp3\)\s*', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'www\.[^\s]+|http\S+|@\s*[^\s]+', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\[www\.[^\]]+\]|\(www\.[^\)]+\)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\[myfreemp3[a-z\.]*\]|\(myfreemp3[a-z\.]*\)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\[mp3freex\]|\(mp3freex\)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\[mp3erger[a-z\.]*\]', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\[\s*320\s*kbps\s*\]|\(\s*320\s*kbps\s*\)|\(\s*128\s*kbps\s*\)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'320\s*kbps|320k|128\s*kbps', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\b(?:1080p|720p|HD|HQ|FULL HD|DVD Quality|Official Video|Official Music Video|Music Video|Official|Lyrics)\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\[(?:HD|HQ|Official|Lyrics|Video)\]|\((?:HD|HQ|Official|Lyrics|Video)\)', '', clean, flags=re.IGNORECASE)

    # Protect 009 Sound System
    is_009 = clean.startswith('009 Sound System')
    if not is_009:
        clean = re.sub(r'^\d{1,3}[\.\-\s_]+', '', clean)

    clean = clean_text(clean)
    clean = re.sub(r'\(\s*\)|\[\s*\]|\{\s*\}', '', clean).strip()

    artist = "Various Artists"
    title = clean

    folder_art = get_folder_artist(folder)

    # Case 1: " - " in clean
    if " - " in clean:
        parts = clean.split(" - ")
        if len(parts) == 2:
            artist = clean_text(parts[0])
            title = clean_text(parts[1])
        elif len(parts) >= 3:
            if parts[0].isdigit() or len(parts[0]) <= 2:
                artist = clean_text(parts[1])
                title = clean_text(" - ".join(parts[2:]))
            elif parts[1].isdigit() or len(parts[1]) <= 2:
                artist = clean_text(parts[0])
                title = clean_text(" - ".join(parts[2:]))
            else:
                artist = clean_text(parts[0])
                title = clean_text(" - ".join(parts[1:]))

    # Case 2: " -- "
    elif " -- " in clean:
        parts = clean.split(" -- ")
        artist = clean_text(parts[0])
        title = clean_text(parts[1])

    # Case 3: " ~ "
    elif " ~ " in clean:
        parts = clean.split(" ~ ")
        artist = clean_text(parts[0])
        title = clean_text(parts[1])

    # Case 4: " by "
    elif " by " in clean.lower():
        pts = re.split(r"\s+by\s+", clean, flags=re.IGNORECASE)
        title = clean_text(pts[0])
        artist = clean_text(pts[1])

    # Case 5: Single hyphen between words with no space e.g. "Bliss-Dunia", "Abdul Qadir-Original"
    elif "-" in clean and " - " not in clean:
        pts = clean.split("-")
        if len(pts) == 2 and len(pts[0]) >= 2 and len(pts[1]) >= 2:
            artist = clean_text(pts[0])
            title = clean_text(pts[1])
        elif len(pts) > 2 and pts[0].isdigit():
            artist = clean_text(pts[1])
            title = clean_text("-".join(pts[2:]))
        elif len(pts) >= 3 and " " not in clean:
            if pts[0].isdigit():
                artist = clean_text(pts[1]).title()
                title = clean_text(" ".join(pts[2:])).title()

    # Case 6: " feat " or " ft " in title
    elif re.search(r'\s+(?:feat\.?|ft\.?)\s+', clean, flags=re.IGNORECASE):
        pts = re.split(r'\s+(?:feat\.?|ft\.?)\s+', clean, maxsplit=1, flags=re.IGNORECASE)
        artist = clean_text(pts[0])
        title = "feat. " + clean_text(pts[1])

    # Case 7: Match known artist prefix / suffix if still Various Artists
    if not artist or artist == "Various Artists":
        cl_low = clean.lower()
        for k_low, k_name in ALL_KNOWN_ARTISTS:
            if cl_low.startswith(k_low):
                rem = clean[len(k_low):].strip(' -_~()[]{}:;,.\'\"')
                if rem and len(rem) >= 2:
                    artist = k_name
                    title = rem
                    break
            elif f" by {k_low}" in cl_low:
                pos = cl_low.find(f" by {k_low}")
                artist = k_name
                title = clean[:pos].strip(' -_~()[]{}:;,.\'\"')
                break
            elif cl_low.endswith(f" {k_low}"):
                pos = len(clean) - len(k_low)
                artist = k_name
                title = clean[:pos].strip(' -_~()[]{}:;,.\'\"')
                break

    # If artist still couldn't be found or is Various Artists, but we have an artist folder:
    if (not artist or artist == "Various Artists") and folder_art:
        artist = folder_art
        title = clean

    title = clean_text(title)
    artist = clean_text(artist)
    if not title: title = clean or base
    if not artist: artist = folder_art or "Various Artists"

    return artist, title

# Taste Classification Sets
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
    'stephan f', 'vitas', 'caravan palace', 'dillon francis', 'fabricio pecanha', 'naxsy', 'remady',
    'manu l', 'touch and go', 'pierce fulton', 'shoffy', 'lincoln jesser', 'twenty one pilots', 'uppermost',
    'otto knows'
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
    'ravi prasad', 'phatjak', 'deepak chopra', 'halimag'
}

def match_artist_keyword(artist, text, artist_set):
    art_l = artist.lower()
    for a in artist_set:
        if len(a) <= 5:
            if re.search(r'\b' + re.escape(a) + r'\b', art_l):
                return True
        else:
            if a in art_l:
                return True
    for a in artist_set:
        if len(a) <= 5:
            if re.search(r'\b' + re.escape(a) + r'\b', text):
                return True
        else:
            if a in text:
                return True
    return False

def classify_track(artist, title, filename, folder, is_in_trance, is_in_gym, is_in_liked):
    text = f"{artist} {title} {filename} {folder}".lower()
    
    if folder == "Desi" or match_artist_keyword(artist, text, DESI_ARTISTS):
        category = "Desi Heritage & Sufi"
        mood = "Desi Soul & Sufi"
        energy = "Medium-High"
        bpm = "85-115 BPM"
        pillar = "Pillar 4: Soulful Desi Heritage & Melodic Sufi / Pop (Weight: 15%)"
        reason = "Deep South Asian vocal acoustics, emotive poetry, and cultural nostalgic soul."
        return category, mood, energy, bpm, pillar, reason

    if "sax" in text or "deep" in folder.lower() or "ehrling" in text or match_artist_keyword(artist, text, DEEP_HOUSE_ARTISTS):
        category = "Sunset Deep House"
        mood = "Sunset Deep House"
        energy = "Medium-High"
        bpm = "120-124 BPM"
        pillar = "Pillar 1: Sunset Deep House & Saxophone Melodic Chill (Weight: 25%)"
        reason = "Warm rolling bassline, organic saxophone/piano hooks, and euphoric sunset dopamine."
        return category, mood, energy, bpm, pillar, reason

    if is_in_trance or "search of sunrise" in text or "elements of life" in text or match_artist_keyword(artist, text, TRANCE_ARTISTS):
        category = "Hypnotic Trance & Balearic"
        mood = "Hypnotic Trance"
        energy = "High"
        bpm = "128-136 BPM"
        pillar = "Pillar 2: Hypnotic Progressive Trance & Sunset Balearic (Weight: 20%)"
        reason = "Expansive progressive synth arpeggios, ethereal breakdowns, and late-night flow state."
        return category, mood, energy, bpm, pillar, reason

    if is_in_gym or match_artist_keyword(artist, text, GYM_EDM_ARTISTS) or "gym" in text:
        category = "Gym Peak Energy"
        mood = "Gym / High Energy"
        energy = "Peak / Explosive"
        bpm = "126-132 BPM"
        pillar = "Pillar 3: High-Energy Gym & Peak Electronic Drive (Weight: 20%)"
        reason = "Driving 4-on-the-floor kick, motivating electronic builds, and PR progressive overload fuel."
        return category, mood, energy, bpm, pillar, reason

    if "buddha" in text or "relax" in text or "nomads" in text or match_artist_keyword(artist, text, LOUNGE_ARTISTS) or artist.lower() == 'ott':
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
    # Tier 1 Manual Downloads: Year-Month folders, Desi Heritage folder, and Root Direct Singles all carry highest 1.5x weight (+12 points)
    if is_ym or is_desi or "Root" in source_tier:
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

def clean_tokens(s):
    return set(re.findall(r'[a-z0-9]{3,}', s.lower()))

IGNORE_WORDS = {'original', 'remix', 'mix', 'edit', 'radio', 'version', 'feat', 'extended', 'club', 'vocal', 'the', 'and', 'for', 'you', 'are', 'with', 'from', 'instrumental', 'dub', 'song', 'lyrics'}

# Scan all audio files
raw_tracks = []

root_files = [f for f in os.listdir(MUSIC_DIR) if os.path.isfile(os.path.join(MUSIC_DIR, f)) and f.lower().endswith(('.mp3', '.m4a', '.flac', '.wav'))]
for f in root_files:
    raw_tracks.append({
        'filename': f,
        'folder': 'Root',
        'is_ym': False,
        'is_desi': False,
        'source_tier': 'Tier 1: Manual Curated (Root Direct Single)'
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

    artist, title = parse_track_name(fn, folder)

    spotify_id = inv_cache.get(fn) or inv_cache.get(fn.lower())
    if not spotify_id:
        clean_fn = re.sub(r'\[.*?\]|\(.*?\)', '', fn).strip()
        spotify_id = inv_cache.get(clean_fn.lower())

    meta = meta_cache.get(spotify_id) if spotify_id else None

    # Validate Spotify match: check for meaningful word overlap
    is_valid_spotify = False
    if meta and meta.get('title'):
        s_title = meta['title']
        fn_tokens = clean_tokens(fn)
        tit_tokens = clean_tokens(title)
        st_tokens = clean_tokens(s_title)
        
        meaningful = ((fn_tokens | tit_tokens) & st_tokens) - IGNORE_WORDS
        if meaningful or ((fn_tokens | tit_tokens) & st_tokens):
            is_valid_spotify = True

    if not is_valid_spotify:
        spotify_id = None
        meta = None

    is_liked = spotify_id in liked_set if spotify_id else False
    is_gym = (spotify_id in gym_set or spotify_id in gym_fast_set) if spotify_id else False
    is_trance = spotify_id in trance_set if spotify_id else False
    is_gym_fast = spotify_id in gym_fast_set if spotify_id else False

    category, mood, energy, bpm, pillar, reason = classify_track(
        artist, title, fn, folder, is_trance, is_gym, is_liked
    )

    taste_match = calculate_taste_match(source_tier, is_ym, is_desi, is_liked, is_gym, is_trance, category, bool(spotify_id))

    norm_artist = re.sub(r'[^a-z0-9]', '', artist.lower())
    norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
    dedup_key = f"{norm_artist}_{norm_title}"
    if not norm_artist or not norm_title or norm_artist == 'variousartists':
        dedup_key = f"{norm_artist}_{re.sub(r'[^a-z0-9]', '', fn.lower())}"

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
        'is_root_manual': (folder == 'Root'),
        'is_ym': is_ym,
        'is_desi': is_desi or (category == 'Desi Heritage & Sufi'),
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
        # Merge flags and highest match
        merged_liked = existing['in_spotify_liked'] or track_obj['in_spotify_liked']
        merged_gym = existing['in_spotify_gym'] or track_obj['in_spotify_gym']
        merged_trance = existing['in_spotify_trance'] or track_obj['in_spotify_trance']
        merged_gym_fast = existing['in_spotify_gym_fast'] or track_obj['in_spotify_gym_fast']
        merged_spotify_id = existing['spotify_id'] or track_obj['spotify_id']
        merged_spotify_uri = existing['spotify_uri'] or track_obj['spotify_uri']
        merged_spotify_url = existing['spotify_url'] or track_obj['spotify_url']
        merged_thumb = existing['thumbnail_url'] if (existing['spotify_id'] and not track_obj['spotify_id']) else track_obj['thumbnail_url']

        # Keep manual download version as primary representation
        if track_obj['is_manual_download'] and not existing['is_manual_download']:
            target = track_obj
            tracks_by_key[dedup_key] = track_obj
        else:
            target = existing

        target['is_manual_download'] = target.get('is_manual_download', False) or track_obj['is_manual_download']
        target['is_root_manual'] = target.get('is_root_manual', False) or track_obj['is_root_manual']
        target['is_ym'] = target.get('is_ym', False) or track_obj['is_ym']
        target['is_desi'] = target.get('is_desi', False) or track_obj['is_desi']
        target['in_spotify_liked'] = merged_liked
        target['in_spotify_gym'] = merged_gym
        target['in_spotify_trance'] = merged_trance
        target['in_spotify_gym_fast'] = merged_gym_fast
        target['spotify_id'] = merged_spotify_id
        target['spotify_uri'] = merged_spotify_uri
        target['spotify_url'] = merged_spotify_url
        target['thumbnail_url'] = merged_thumb

        # If merged target is a manual download, ensure source_tier reflects Tier 1
        if target['is_root_manual'] and 'Root' not in target.get('source_tier', ''):
            target['source_tier'] = 'Tier 1: Manual Curated (Root Direct Single)'
        elif (target['is_ym'] or target['is_desi']) and 'Tier 1' not in target.get('source_tier', ''):
            target['source_tier'] = f"Tier 1: Manual Curated ({target.get('source_folder', 'Archive')})"

        # Recalculate taste match using complete merged flags
        target['taste_match'] = calculate_taste_match(
            target.get('source_tier', ''),
            target.get('is_ym', False),
            target.get('is_desi', False),
            target.get('in_spotify_liked', False),
            target.get('in_spotify_gym', False),
            target.get('in_spotify_trance', False),
            target.get('category', ''),
            bool(target.get('spotify_id'))
        )


unified_tracks = list(tracks_by_key.values())
unified_tracks.sort(key=lambda t: (-t['taste_match'], t['artist'].lower(), t['title'].lower()))

category_counts = Counter(t['category'] for t in unified_tracks)
mood_counts = Counter(t['mood'] for t in unified_tracks)
manual_count = sum(1 for t in unified_tracks if t.get('is_manual_download'))
root_count = sum(1 for t in unified_tracks if t.get('is_root_manual'))
ym_count = sum(1 for t in unified_tracks if t.get('is_ym'))
desi_count = sum(1 for t in unified_tracks if t.get('is_desi'))
spotify_matched_count = sum(1 for t in unified_tracks if t['spotify_id'])
liked_count = sum(1 for t in unified_tracks if t['in_spotify_liked'])
gym_count = sum(1 for t in unified_tracks if t['in_spotify_gym'])
trance_count = sum(1 for t in unified_tracks if t['in_spotify_trance'])

database_payload = {
    'metadata': {
        'catalog_name': "Sikander's Master Music Intelligence & Taste Catalog",
        'generated_at': "2026-09-13T01:35:00+05:00",
        'total_tracks': len(unified_tracks),
        'manual_downloads_count': manual_count,
        'manual_root_count': root_count,
        'manual_ym_count': ym_count,
        'desi_count': desi_count,
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

# 1. Output JSON
out_json_file = os.path.join(DATA_DIR, "sikander_music_library.json")
with open(out_json_file, "w", encoding="utf-8") as f:
    json.dump(database_payload, f, indent=2, ensure_ascii=False)

# 2. Output JS for offline / local file protocol
out_js_file = os.path.join(DATA_DIR, "sikander_music_library.js")
with open(out_js_file, "w", encoding="utf-8") as f:
    f.write("window.SIKANDER_MUSIC_DATA = " + json.dumps(database_payload, ensure_ascii=False) + ";\n")

print(f"Successfully wrote master database to {out_json_file} ({os.path.getsize(out_json_file)} bytes)")
print(f"Successfully wrote standalone JS database to {out_js_file} ({os.path.getsize(out_js_file)} bytes)")
print(f"Total deduplicated tracks: {len(unified_tracks)}")
print(f"Manual Year-Month tracks: {ym_count}, Desi tracks: {desi_count}, Total manual archive picks: {manual_count}")
print(f"Verified Spotify matches: {spotify_matched_count}")
print("Category distribution:", dict(category_counts))
print("Mood distribution:", dict(mood_counts))

# 3. Automatically generate Spotify playlist exports & guides
exporter_script = os.path.join(DATA_DIR, "export_spotify_playlists.py")
if os.path.exists(exporter_script):
    import subprocess
    print("Triggering Spotify playlist exports...")
    subprocess.run([sys.executable, exporter_script], check=True)
