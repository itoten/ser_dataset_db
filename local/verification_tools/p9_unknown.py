"""For each dataset gap, search the cached text of its primary sources broadly; no hit = candidate 'unknown', hit = manual list."""
import csv, json, os, re, sys, collections
S = {s['source_id']: s for s in csv.DictReader(open('data/sources.csv'))}
L = list(csv.DictReader(open('data/dataset_sources.csv')))
D = {d['dataset_id']: d for d in csv.DictReader(open('data/datasets.csv'))}
A = json.load(open('local/verification_tools/abstracts.json'))
def text(sid):
    t = ''
    p = f'local/p9_results/{sid}.json'
    if os.path.exists(p):
        try: t += json.load(open(p)).get('text', '') or ''
        except Exception: pass
    p = f'local/scan_cache/{sid}.txt'
    if os.path.exists(p): t += ' ' + open(p, errors='replace').read()
    a = A.get(sid, '')
    if a and not a.startswith('ERR'): t += ' ' + a
    return re.sub(r'\s+', ' ', t)
N = r'(?:\d[\d,.]*|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|hundred|thousand)'
NS = r'\d[\d,.]*'
PAT = {
 'n_files_reported': rf'{NS}\s+(?:\w+\s+){{0,3}}(?:utterances?|clips?|recordings?|files?|samples?|sentences?|audios?|videos?|instances?|segments?|dialogu?es?|stimuli|tokens|items|takes|calls|turns|words)',
 'hours_reported': rf'{NS}\s*(?:hours?|hrs?|minutes?|mins?)\b',
 'n_speakers_reported': rf'{N}\s+(?:\w+\s+){{0,3}}(?:speakers?|subjects?|participants?|actors?|actresses|volunteers?|students?|children|people|persons?|males?|females?|men|women|informants?|talkers|individuals|artists|singers|narrators?)',
 'speech_production': r'\b(?:acted|actors?|actresses|spontaneous\w*|elicit\w*|induced|improvis\w*|simulated|portray\w*|enact\w*|read speech|read aloud|natural conversations?|real[- ]life)',
 'license_spdx': r'(?i:licen[sc]e\w*|CC[ -]BY|creative commons|public domain|non-?commercial|terms of use)',
 'access_method': r'(?i:download\w*|upon request|on request|request access|agreement|e-?mail us|contact (?:us|the)|apply)',
 'languages': '|'.join(['English','German','French','Spanish','Italian','Portuguese','Russian','Polish','Czech','Turkish','Arabic','Chinese','Mandarin','Cantonese','Japanese','Korean','Hindi','Bengali','Bangla','Tamil','Telugu','Kannada','Malayalam','Marathi','Gujarati','Punjabi','Urdu','Persian','Farsi','Hebrew','Thai','Vietnamese','Indonesian','Javanese','Swedish','Danish','Dutch','Hungarian','Romanian','Greek','Finnish','Kurdish','Burmese','Afrikaans','Assamese','Amharic','Kazakh','Filipino','Tagalog','Sinhala','Nepali','Khmer','Mongolian','Serbian','Croatian','Slovak','Slovenian','Bulgarian','Ukrainian','Lithuanian','Estonian','Latvian','Icelandic','Norwegian','Catalan','Basque','Swahili','Hausa','Yoruba','Zulu','Quechua','Sindhi','Pashto','Odia','Albanian','Georgian','Armenian']),
}
res = collections.defaultdict(dict)
for d, row in D.items():
    srcs = [l['source_id'] for l in L if l['dataset_id'] == d and S[l['source_id']]['source_type'] == 'primary']
    texts = [(s, text(s)) for s in dict.fromkeys(srcs)]
    texts = [(s, t) for s, t in texts if len(t) > 1500 and len(re.findall(r'emotion|affect|speech|audio', t, re.I)) >= 5]
    if not texts: continue
    main = max(texts, key=lambda x: len(x[1]))[0]
    for f, pat in PAT.items():
        if row[f] != '': continue
        hit = any(re.search(pat, t, re.I if f != 'languages' else 0) for _, t in texts)
        res[d][f] = ('hit' if hit else 'none', main)
json.dump(res, open('local/verification_tools/p9_unknown.json', 'w'))
c = collections.Counter(v[0] for d in res.values() for v in d.values())
print(c, len(res))
