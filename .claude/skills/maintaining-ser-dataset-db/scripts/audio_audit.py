"""Independent checks of a corpus's audio files: inventory and duplicate detection.

Needs numpy and soundfile (scipy and pyarrow are optional, see below). Run it in the Python
environment that has them (usually the speech toolkit's environment, not the system Python).

    python audio_audit.py inventory DIR
        Files per extension, readable audio, formats (sample rate, channels, subtype),
        durations, and groups of byte-identical files (MD5).

    python audio_audit.py dups DIR [--out pairs.tsv]
        Near-identical audio inside DIR: same sound, different bytes (re-encoded, trimmed by a
        few samples, copied under another name or label).

    python audio_audit.py dups DIR --against OTHER_DIR
        The same check between two corpora (e.g. "does corpus A reuse clips of corpus B?").

Audio is read from every file soundfile can open, and from Hugging Face style parquet files
(an `audio` column holding {"bytes", "path"}) when pyarrow is installed.

How `dups` works, and why the defaults are what they are:
  1. Every clip is reduced to mono 16 kHz and summarised by its duration and a 100-bin
     log-energy envelope. Only these summaries are kept in memory.
  2. Candidate pairs: durations within --dur-tol seconds AND envelope correlation >= --prefilter.
     The prefilter is deliberately loose. A tight value (0.97) once missed a true duplicate
     whose envelope scored lower than its waveform did; the exact check in step 3 is what decides.
  3. Each candidate is verified with the normalised waveform cross-correlation over lags up to
     --max-lag-ms. Pairs at or above --threshold are reported as near-identical; pairs between
     0.90 and the threshold are listed as borderline for a human to judge.
Byte-identical files are found by `inventory`; `dups` also reports them (correlation 1.0).
"""

import argparse
import collections
import hashlib
import io
import statistics
import sys
from pathlib import Path

try:
    import numpy as np
    import soundfile as sf
except ImportError as e:  # pragma: no cover
    raise SystemExit(f"audio_audit needs numpy and soundfile ({e}). Run it in the toolkit's environment.")

try:
    from scipy.signal import resample_poly
except ImportError:
    resample_poly = None

# 16 kHz keeps the speech band and makes clips stored at different native rates comparable.
TARGET_SR = 16000
# 100 envelope bins resolve about 30 ms on a 3-second clip, enough to separate different takes.
N_BINS = 100
# Rows of the envelope matrix compared per block; bounds memory to about BLOCK * N * 4 bytes.
BLOCK = 2048
# Borderline band printed for human review, below the acceptance threshold.
BORDERLINE = 0.90

AUDIO_EXT = {".wav", ".flac", ".ogg", ".oga", ".aiff", ".aif", ".mp3", ".opus"}


# --------------------------------------------------------------------------------------------
# reading

def iter_sources(root):
    """Yield (name, loader) for every clip under root. loader() returns raw bytes."""
    root = Path(root)
    if not root.exists():
        raise SystemExit(f"no such directory: {root}")
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in AUDIO_EXT:
            yield str(p.relative_to(root)), (lambda p=p: p.read_bytes())
        elif ext == ".parquet":
            try:
                import pyarrow.parquet as pq
            except ImportError:
                print(f"skip {p.name}: install pyarrow to read parquet", file=sys.stderr)
                continue
            table = pq.read_table(p, columns=["audio"]).to_pylist()
            for i, r in enumerate(table):
                a = r["audio"] or {}
                name = f"{p.relative_to(root)}#{i}:{a.get('path') or ''}"
                yield name, (lambda b=a.get("bytes"): b)


def decode(raw):
    """Bytes -> (mono float32 at TARGET_SR, native sample rate, info)."""
    info = sf.info(io.BytesIO(raw))
    x, sr = sf.read(io.BytesIO(raw), dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    if sr != TARGET_SR:
        if resample_poly is not None:
            g = np.gcd(sr, TARGET_SR)
            x = resample_poly(x, TARGET_SR // g, sr // g).astype(np.float32)
        else:  # linear interpolation is enough for a similarity check
            t = np.arange(0, len(x) / sr, 1 / TARGET_SR)
            x = np.interp(t, np.arange(len(x)) / sr, x).astype(np.float32)
    return x, sr, info


def envelope(x):
    n = len(x) // N_BINS * N_BINS
    if n < N_BINS:
        return np.zeros(N_BINS, dtype=np.float32)
    e = np.log1p((x[:n].reshape(N_BINS, -1) ** 2).mean(axis=1) * 1e4)
    e = e - e.mean()
    return (e / (np.linalg.norm(e) + 1e-9)).astype(np.float32)


# --------------------------------------------------------------------------------------------
# inventory

def inventory(args):
    root = Path(args.dir)
    ext = collections.Counter(p.suffix.lower() or "(none)" for p in root.rglob("*") if p.is_file())
    fmt = collections.Counter()
    durs, bad = [], []
    md5 = collections.defaultdict(list)
    for name, load in iter_sources(root):
        raw = load()
        if not raw:
            bad.append((name, "empty"))
            continue
        md5[hashlib.md5(raw).hexdigest()].append(name)
        try:
            info = sf.info(io.BytesIO(raw))
        except Exception as e:  # unreadable files are reported, not fatal
            bad.append((name, str(e)[:80]))
            continue
        fmt[(info.samplerate, info.channels, info.subtype)] += 1
        durs.append(info.duration)
    print(f"files by extension: {dict(ext)}")
    print(f"readable clips: {len(durs)}   unreadable: {len(bad)}")
    for name, why in bad[:20]:
        print(f"  unreadable {name}: {why}")
    print(f"formats (sample rate, channels, subtype): {dict(fmt)}")
    if durs:
        print(f"duration s: min {min(durs):.3f}  median {statistics.median(durs):.3f}  "
              f"max {max(durs):.3f}  total {sum(durs) / 3600:.4f} h")
    groups = [v for v in md5.values() if len(v) > 1]
    print(f"byte-identical groups: {len(groups)}  files in them: {sum(map(len, groups))}  "
          f"redundant copies: {sum(len(v) - 1 for v in groups)}")
    for g in groups[: args.show]:
        print("  " + "  |  ".join(g))


# --------------------------------------------------------------------------------------------
# near-duplicates

def summarise(root):
    names, loaders, durs, envs = [], [], [], []
    for name, load in iter_sources(root):
        raw = load()
        if not raw:
            continue
        try:
            x, _, _ = decode(raw)
        except Exception as e:
            print(f"skip unreadable {name}: {str(e)[:80]}", file=sys.stderr)
            continue
        names.append(name)
        loaders.append(load)
        durs.append(len(x) / TARGET_SR)
        envs.append(envelope(x))
    if not names:
        raise SystemExit(f"no readable audio under {root}")
    return names, loaders, np.array(durs), np.stack(envs)


def best_corr(a, b, max_lag):
    """Max normalised cross-correlation of a and b over lags in [-max_lag, max_lag] samples."""
    n = min(len(a), len(b))
    a, b = a[:n].astype(np.float64), b[:n].astype(np.float64)
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom == 0:
        return 0.0, 0
    size = 1 << (2 * n - 1).bit_length()
    cc = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(b, size)), size)
    lags = np.concatenate([np.arange(0, max_lag + 1), np.arange(-max_lag, 0)])
    vals = cc[lags % size]
    i = int(np.argmax(vals))
    return float(vals[i] / denom), int(lags[i])


def dups(args):
    A = summarise(args.dir)
    B = summarise(args.against) if args.against else A
    same = args.against is None
    print(f"clips: {len(A[0])}" + ("" if same else f" vs {len(B[0])}"), file=sys.stderr)

    cand = []
    for s in range(0, len(A[0]), BLOCK):
        S = A[3][s:s + BLOCK] @ B[3].T
        D = np.abs(A[2][s:s + BLOCK, None] - B[2][None, :])
        ok = (S >= args.prefilter) & (D <= args.dur_tol)
        ii, jj = np.nonzero(ok)
        for i, j in zip(ii + s, jj):
            if not same or i < j:
                cand.append((i, j))
    print(f"candidates after prefilter: {len(cand)}", file=sys.stderr)

    cache = {}

    def clip(side, k):
        key = (side, k)
        if key not in cache:
            if len(cache) > args.cache:
                cache.clear()
            cache[key] = decode(((A if side == "a" else B)[1][k])())[0]
        return cache[key]

    max_lag = int(args.max_lag_ms * TARGET_SR / 1000)
    hits, border = [], []
    for i, j in cand:
        c, lag = best_corr(clip("a", i), clip("b", j), max_lag)
        row = (A[0][i], B[0][j], c, lag * 1000 / TARGET_SR, A[2][i], B[2][j])
        if c >= args.threshold:
            hits.append(row)
        elif c >= BORDERLINE:
            border.append(row)

    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, *_ in hits:
        parent[find(a)] = find(b)
    groups = collections.defaultdict(set)
    for a, b, *_ in hits:
        groups[find(a)].update([a, b])
    files = sum(len(g) for g in groups.values())
    print(f"near-identical pairs (corr >= {args.threshold}): {len(hits)}")
    print(f"groups: {len(groups)}  files in groups: {files}  redundant copies: {files - len(groups)}")
    print(f"borderline pairs ({BORDERLINE} <= corr < {args.threshold}), review by ear: {len(border)}")
    lines = ["kind\tclip_a\tclip_b\tcorr\tlag_ms\tdur_a\tdur_b"]
    for kind, rows in (("dup", hits), ("borderline", border)):
        for a, b, c, lag, da, db in sorted(rows, key=lambda r: -r[2]):
            lines.append(f"{kind}\t{a}\t{b}\t{c:.4f}\t{lag:.2f}\t{da:.3f}\t{db:.3f}")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"pairs written to {args.out}")
    else:
        print(text, end="")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory")
    p.add_argument("dir")
    p.add_argument("--show", type=int, default=10, help="byte-identical groups to print")
    p.set_defaults(func=inventory)
    p = sub.add_parser("dups")
    p.add_argument("dir")
    p.add_argument("--against", help="compare DIR with this corpus instead of with itself")
    # Same sound copied or re-encoded scores > 0.99; different takes of the same sentence by the
    # same speaker stay far below. 0.98 leaves room for lossy re-encoding.
    p.add_argument("--threshold", type=float, default=0.98)
    p.add_argument("--prefilter", type=float, default=0.80, help="envelope correlation for candidates (keep loose)")
    # Copies trimmed or padded by a few frames differ by tens of milliseconds at most.
    p.add_argument("--dur-tol", type=float, default=0.05, help="max duration difference in seconds")
    # Cuts of the same recording shifted by a few milliseconds still count as the same sound.
    p.add_argument("--max-lag-ms", type=float, default=10.0)
    p.add_argument("--cache", type=int, default=20000, help="decoded clips kept in memory")
    p.add_argument("--out", help="write the pair list (TSV) here instead of stdout")
    p.set_defaults(func=dups)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
