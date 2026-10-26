"""Whisper large-v3 transcripts of a few clips per sentence code (file names <speaker>_<CODE>_<EMO>_<LANG>.wav), to compare the wording across corpora.

Run in the espnet pixi env: pixi run python sentence_code_whisper_sample.py CORPUS_DIR LANG OUT.tsv
(LANG is the Whisper language code, en or es)."""
import glob, os, random, sys
import librosa, torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor
corpus, lang, out = sys.argv[1:4]
proc = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3", torch_dtype=torch.float16).cuda().eval()
files = sorted(glob.glob(os.path.join(corpus, "*.wav")))
by = {}
for f in files:
    by.setdefault(os.path.basename(f).split("_")[1], []).append(f)
random.seed(1)
with open(out, "w") as fh:
    fh.write("file\tcode\twhisper_large_v3\n")
    for code in sorted(by):
        for f in random.sample(by[code], 6):
            x, _ = librosa.load(f, sr=16000, mono=True)
            feats = proc(x, sampling_rate=16000, return_tensors="pt").input_features.cuda().half()
            with torch.no_grad():
                ids = model.generate(feats, language=lang, task="transcribe", max_new_tokens=60)
            fh.write(f"{os.path.basename(f)}\t{code}\t{proc.batch_decode(ids, skip_special_tokens=True)[0].strip()}\n")
