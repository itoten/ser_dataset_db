"""Whisper large-v3 transcripts of a sample of baser and cbesd (English), to see whether a sentence number means the same text in every emotion.

Run in the espnet pixi env: pixi run python whisper_sample.py OUT.tsv (audio under ~/data/<corpus>)."""
import glob, os, random, re, sys
import librosa, torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor
proc = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3", torch_dtype=torch.float16).cuda().eval()
def tx(path, lang):
    x, _ = librosa.load(path, sr=16000, mono=True)
    f = proc(x, sampling_rate=16000, return_tensors="pt").input_features.cuda().half()
    with torch.no_grad():
        ids = model.generate(f, language=lang, task="transcribe", max_new_tokens=120)
    return proc.batch_decode(ids, skip_special_tokens=True)[0].strip()
D = os.path.expanduser("~/data")
out = sys.argv[1]
rows = []
# baser: speakers HASAN (M) and CHAITY (F), take 1, sentences S_1..S_5 x 5 emotions
for spk in ("M_1_HASAN", "F_1_CHAITY"):
    for p in sorted(glob.glob(f"{D}/baser/BASER_DATASET/{spk}_S_*_*_1.wav")):
        m = re.search(r"_S_(\d)_([A-Z]+)_1", p)
        rows.append(("baser", os.path.basename(p), f"S_{m.group(1)}", m.group(2), tx(p, "bn")))
# cbesd English: 3 random children per (emotion, utterance number)
random.seed(0)
for emo in ("ANGRY", "DISGUST", "FEAR", "HAPPY", "NEUTRAL", "SAD"):
    files = glob.glob(f"{D}/cbesd/BESD/ENGLISH/{emo}/*.wav")
    for n in range(1, 6):
        cand = sorted(f for f in files if re.search(rf"_{n}\.wav$", f))
        for p in random.sample(cand, min(3, len(cand))):
            rows.append(("cbesd", os.path.basename(p), f"utt_{n}", emo, tx(p, "en")))
with open(out, "w") as fh:
    fh.write("dataset\tfile\tsentence_id\temotion\twhisper_large_v3\n")
    for r in rows: fh.write("\t".join(r) + "\n")
print(len(rows))
