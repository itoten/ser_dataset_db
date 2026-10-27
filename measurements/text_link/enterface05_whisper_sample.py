"""Whisper large-v3 transcripts of all clips of two subjects of eNTERFACE'05 (converted wav of the recipe), to see which sentences are read in which emotion.

Run in the espnet pixi env: pixi run python enterface05_whisper_sample.py WAV_DIR OUT.tsv (WAV_DIR holds the converted wav named enterface05-<subject>-<emotion>-<n>.wav)."""
import glob, os, sys, re
import librosa, torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor
wav_dir, out = sys.argv[1:3]
proc = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3", torch_dtype=torch.float16).cuda().eval()
files = sorted(f for f in glob.glob(os.path.join(wav_dir, "*.wav")) if re.search(r"-s(1|2)-", os.path.basename(f)))
with open(out, "w") as fh:
    fh.write("file\twhisper_large_v3\n")
    for f in files:
        x, _ = librosa.load(f, sr=16000, mono=True)
        feats = proc(x, sampling_rate=16000, return_tensors="pt").input_features.cuda().half()
        with torch.no_grad():
            ids = model.generate(feats, language="en", task="transcribe", max_new_tokens=60)
        fh.write(f"{os.path.basename(f)}\t{proc.batch_decode(ids, skip_special_tokens=True)[0].strip()}\n")
