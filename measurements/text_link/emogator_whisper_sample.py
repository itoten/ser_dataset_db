"""Whisper large-v3 transcripts of 20 random EmoGator clips per category, to look for spoken words (e.g. category names).

Run in the espnet pixi env: pixi run python emogator_whisper_sample.py MP3_DIR OUT.tsv
(MP3_DIR = data/mp3 of the EmoGator repository)."""
import collections, glob, os, random, sys
import librosa, torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor
proc = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3", torch_dtype=torch.float16).cuda().eval()
files = sorted(glob.glob(os.path.join(sys.argv[1], "*.mp3")))
by_cat = collections.defaultdict(list)
for f in files:
    by_cat[os.path.basename(f).split("-")[1]].append(f)
random.seed(0)
with open(sys.argv[2], "w") as fh:
    fh.write("file\tcategory_id\twhisper_large_v3\n")
    for cat in sorted(by_cat):
        for f in random.sample(by_cat[cat], 20):
            x, _ = librosa.load(f, sr=16000, mono=True)
            feats = proc(x, sampling_rate=16000, return_tensors="pt").input_features.cuda().half()
            with torch.no_grad():
                ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=40)
            fh.write(f"{os.path.basename(f)}\t{cat}\t{proc.batch_decode(ids, skip_special_tokens=True)[0].strip()}\n")
