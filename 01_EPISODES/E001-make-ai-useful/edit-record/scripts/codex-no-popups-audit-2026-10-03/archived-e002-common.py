#!/usr/bin/env python3
"""Shared helpers for jtan's Episode 002 hook testers and full theme cut.

Source: the unchanged September 26 reshoot. Every cut is a frame boundary chosen
at the quietest point between two words (whisper word timings + audio envelope).
Audio: both mics centered in both ears (the raw pans Josh and Mary apart), 70 Hz
high-pass, gentle leveling, then one linear loudness pass over the whole raw so
every hook and the full episode share identical dialogue processing.
"""

import hashlib
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parents[1]
ROOT = EPISODE.parents[1]
RAW = Path("/Users/je/Movies/Episode 2 Raw.mp4")
RAW_SHA = "087b52c20549f20118216a867005944948da8d39f013b3089789a987aa79b42d"
CARDS = EPISODE / "edit/jtan-cards-002/out"
MUSIC = ROOT / "03_ASSETS/music"
WORK = Path("/private/tmp/claude-501/-Users-je-jtan/95a08390-3916-473d-aa4d-e7994b3cd5bf/scratchpad/e2")
WORDS_JSON = WORK / "rawdtw.json"
ENV_WAV = WORK / "raw.wav"
DIALOGUE = WORK / "dialogue-processed.wav"

FPS = 30
TITLE_FRAMES = 158   # 5.267 s, same as Episode 000
OUTRO_FRAMES = 323   # 10.767 s, same as Episode 000
PRE = ("highpass=f=70,"
       "pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1,"
       "dynaudnorm=f=300:g=15:p=0.85:m=3")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check_raw():
    if not RAW.is_file() or sha256(RAW) != RAW_SHA:
        raise RuntimeError("Episode 2 raw is missing or changed")


# ---------- words and quiet points ----------

def load_words():
    """Words with punctuation; start = DTW time of the word's first token."""
    d = json.loads(WORDS_JSON.read_text())
    words = []
    for seg in d["transcription"]:
        for t in seg.get("tokens", []):
            tx = t["text"]
            if tx.startswith("[_") or not tx.strip():
                continue
            dtw = t.get("t_dtw", -1)
            a = dtw / 100 if dtw is not None and dtw >= 0 else t["offsets"]["from"] / 1000
            b = t["offsets"]["to"] / 1000
            if tx.startswith(" ") or not words:
                words.append([tx.strip(), a, b])
            else:
                words[-1][0] += tx
                words[-1][2] = max(words[-1][2], b)
    words = [w for w in words if w[0].strip()]
    for i in range(len(words) - 1):  # a word ends no later than the next one starts
        words[i][2] = min(max(words[i][2], words[i][1] + 0.05), words[i + 1][1])
    return [tuple(w) for w in words]


WORDS = None
NORM = None


def _norm(s):
    return re.sub(r"[^a-z0-9']", "", s.lower())


def words():
    global WORDS, NORM
    if WORDS is None:
        WORDS = load_words()
        NORM = [_norm(w) for w, _, _ in WORDS]
    return WORDS


def find(phrase, near, window=25):
    """Return (first_index, start_s, end_s) of the phrase occurrence nearest `near`."""
    W = words()
    p = [_norm(x) for x in phrase.split()]
    hits = [i for i in range(len(W) - len(p) + 1)
            if NORM[i:i + len(p)] == p and abs(W[i][1] - near) < window]
    if not hits:
        raise ValueError(f"not found near {near}: {phrase}")
    i = min(hits, key=lambda h: abs(W[h][1] - near))
    return i, W[i][1], W[i + len(p) - 1][2]


_ENV = None


def envelope():
    """RMS dB per 5 ms of the centered mono mix at 16 kHz."""
    global _ENV
    if _ENV is None:
        w = wave.open(str(ENV_WAV))
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        hop = 80
        n = len(x) // hop
        x = x[:n * hop].reshape(n, hop)
        _ENV = 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)
    return _ENV


SILENT_DB = -46.0   # speech sits near -30 dB; gaps between words fall below -50
MIN_RUN = 0.05
WARNINGS = []


def _runs(lo, hi):
    env = envelope()
    a, b = max(0, int(lo / 0.005)), int(hi / 0.005)
    low = env[a:b] < SILENT_DB
    runs, i = [], 0
    while i < len(low):
        if low[i]:
            j = i
            while j < len(low) and low[j]:
                j += 1
            if (j - i) * 0.005 >= MIN_RUN:
                runs.append(((a + i) * 0.005, (a + j) * 0.005))
            i = j
        else:
            i += 1
    return runs


def _snap(target, run):
    k = round(target * FPS)
    if run and not (run[0] <= k / FPS <= run[1]):
        inside = [x for x in (int(np.ceil(run[0] * FPS)), int(np.floor(run[1] * FPS)))
                  if run[0] <= x / FPS <= run[1]]
        if inside:
            k = min(inside, key=lambda x: abs(x / FPS - target))
    return k


def quiet_frame(lo, hi):
    """Quietest frame in [lo, hi] (fallback when no silent run exists)."""
    env = envelope()
    best = None
    for k in range(int(np.ceil(lo * FPS)), int(np.floor(hi * FPS)) + 1):
        c = int(k / FPS / 0.005)
        e = float(env[max(0, c - 4):c + 5].max())
        if best is None or e < best[0]:
            best = (e, k)
    return best[1] if best else round((lo + hi) / 2 * FPS)


def cut_after(phrase, near):
    """Frame ~50 ms into the silence that follows `phrase`."""
    W = words()
    i, _, _ = find(phrase, near)
    last = W[i + len(phrase.split()) - 1]
    nxt = W[i + len(phrase.split())][1] if i + len(phrase.split()) < len(W) else last[2] + 1
    lo, hi = last[1] + 0.08, max(nxt + 0.15, last[1] + 0.5)
    runs = _runs(lo, hi)
    if not runs:
        WARNINGS.append(f"no silence after '{phrase}' near {near}")
        return quiet_frame(lo, hi)
    run = max(runs, key=lambda r: r[1] - r[0])
    return _snap(run[0] + min(0.05, (run[1] - run[0]) / 3), run)


def cut_before(phrase, near):
    """Frame ~50 ms before `phrase` begins, inside the preceding silence."""
    W = words()
    i, start, _ = find(phrase, near)
    prv = W[i - 1][1] if i > 0 else max(0.0, start - 3)
    lo, hi = min(prv + 0.08, start - 0.3), start + 0.12
    runs = _runs(lo, hi)
    if not runs:
        WARNINGS.append(f"no silence before '{phrase}' near {near}")
        return quiet_frame(lo, hi)
    run = max(runs, key=lambda r: r[1] - r[0])
    return _snap(run[1] - min(0.05, (run[1] - run[0]) / 3), run)


# ---------- audio ----------

def build_dialogue():
    """Centered, leveled, loudness-normalized dialogue for the whole raw (48 kHz s24)."""
    if DIALOGUE.exists():
        return DIALOGUE
    probe = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-i", str(RAW), "-map", "0:1",
         "-af", PRE + ",loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True).stderr
    stats = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={stats['input_i']}:"
          f"measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
          f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true")
    tmp = DIALOGUE.with_suffix(".part.wav")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(RAW), "-map", "0:1",
                    "-af", PRE + "," + ln + ",aresample=48000", "-c:a", "pcm_s24le", str(tmp)],
                   check=True)
    tmp.rename(DIALOGUE)
    (WORK / "dialogue-loudnorm-pass1.json").write_text(json.dumps(stats, indent=1))
    return DIALOGUE


# ---------- render ----------

def inputs_of(args):
    return [x for i, x in enumerate(args) if i and args[i - 1] == "-i"]


def render(pieces, output, height=1080, crf=18, chapters=None, title=None):
    """pieces: ("src", first_frame, end_frame_exclusive) | ("intro",) | ("outro",).

    Source picture comes from the raw; source audio from the processed dialogue,
    with 8 ms ramps at every source edge. Refuses to overwrite.
    """
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    build_dialogue()
    inputs = ["-loop", "1", "-framerate", "30", "-i", str(CARDS / "intro-card.png"),
              "-i", str(MUSIC / "oood-sting-5s.wav"),
              "-loop", "1", "-framerate", "30", "-i", str(CARDS / "outro-card.png"),
              "-i", str(MUSIC / "oood-outro-11s.wav")]
    scale = f",scale=-2:{height}:flags=lanczos" if height != 1080 else ""
    f, labels, total = [], [], 0
    for n, p in enumerate(pieces):
        if p[0] == "src":
            a, b = p[1], p[2]
            fo = p[3] if len(p) > 3 else 0.008   # optional longer fade-out for overlapped speech
            d = (b - a) / FPS
            vi, ai = len(inputs_of(inputs)), len(inputs_of(inputs)) + 1
            # per-segment input seek: frame a is the first frame at/after (a - 0.5)/30
            inputs += ["-ss", f"{(a - 0.5) / FPS:.6f}", "-t", f"{d + 1:.6f}", "-i", str(RAW),
                       "-ss", f"{a / FPS:.6f}", "-t", f"{d + 0.5:.6f}", "-i", str(DIALOGUE)]
            f.append(f"[{vi}:v]trim=end_frame={b - a},setpts=N/(30*TB),"
                     f"format=yuv420p,setsar=1{scale}[v{n}]")
            f.append(f"[{ai}:a]atrim=end_sample={round(d * 48000)},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.008,afade=t=out:st={d - fo:.6f}:d={fo},"
                     f"apad,atrim=duration={d:.6f}[a{n}]")
            total += b - a
        elif p[0] == "intro":
            d = TITLE_FRAMES / FPS
            f.append(f"[0:v]trim=end_frame={TITLE_FRAMES},setpts=N/(30*TB),format=yuv420p,setsar=1{scale}[v{n}]")
            f.append(f"[1:a]volume=-1.6dB,aresample=48000,apad,atrim=duration={d:.6f}[a{n}]")
            total += TITLE_FRAMES
        elif p[0] == "outro":
            d = OUTRO_FRAMES / FPS
            f.append(f"[2:v]trim=end_frame={OUTRO_FRAMES},setpts=N/(30*TB),format=yuv420p,setsar=1{scale},"
                     f"fade=t=out:st={d - 0.5:.6f}:d=0.5[v{n}]")
            f.append(f"[3:a]volume=-3.3dB,aresample=48000,apad,atrim=duration={d:.6f},"
                     f"afade=t=out:st={d - 0.7:.6f}:d=0.7[a{n}]")
            total += OUTRO_FRAMES
        labels.append(f"[v{n}][a{n}]")
    f.append("".join(labels) + f"concat=n={len(pieces)}:v=1:a=1[v][a]")
    graph_file = output.with_suffix(".filtergraph.txt")
    graph_file.write_text(";\n".join(f))
    meta = []
    if chapters or title:
        mf = output.with_suffix(".ffmeta")
        lines = [";FFMETADATA1"]
        if title:
            lines += [f"title={title}", "artist=Josh and Mary"]
        end = total / FPS
        for i, (start, name) in enumerate(chapters or []):
            stop = chapters[i + 1][0] if i + 1 < len(chapters) else end
            lines += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={round(start * 1000)}",
                      f"END={round(stop * 1000)}", f"title={name}"]
        mf.write_text("\n".join(lines) + "\n")
        meta = ["-map_metadata", str(len(inputs_of(inputs))), "-map_chapters", str(len(inputs_of(inputs)))]
        inputs += ["-i", str(mf)]
    part = output.with_name(output.stem + ".part.mp4")
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y", *inputs,
           "-filter_complex_script", str(graph_file), "-map", "[v]", "-map", "[a]", *meta,
           "-frames:v", str(total), "-r", "30", "-fps_mode", "cfr",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-colorspace", "bt709", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
           str(part)]
    subprocess.run(cmd, check=True)
    part.rename(output)
    graph_file.unlink()
    return total


# ---------- punctuated caption words ----------

PUNCT_SRT = WORK / "raw-punctuated-0926.srt"


def caption_words():
    """Punctuated, cased words from the 9/26 transcript, timed by the DTW words."""
    import difflib
    text = []
    for block in re.split(r"\n\s*\n", PUNCT_SRT.read_text().strip()):
        text += " ".join(block.splitlines()[2:]).split()
    W = words()
    a = [_norm(t) for t in text]
    b = [_norm(w) for w, _, _ in W]
    times = [None] * len(text)
    for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(m.size):
            times[m.a + k] = (W[m.b + k][1], W[m.b + k][2])
    known = [i for i, t in enumerate(times) if t]
    for i, t in enumerate(times):
        if t is None:
            lo = max([k for k in known if k < i], default=None)
            hi = min([k for k in known if k > i], default=None)
            t0 = times[lo][1] if lo is not None else times[hi][0]
            t1 = times[hi][0] if hi is not None else t0 + 0.3
            span = [j for j in range((lo if lo is not None else -1) + 1, hi if hi is not None else len(text))]
            f = (span.index(i) + 0.5) / len(span)
            times[i] = (t0 + (t1 - t0) * f, t0 + (t1 - t0) * f + 0.05)
    out = []
    for i, (w, (s, e)) in enumerate(zip(text, times)):
        nxt = times[i + 1][0] if i + 1 < len(times) else s + 0.5
        out.append((w, s, max(s + 0.05, min(nxt, s + 0.6))))  # DTW gives starts, not ends
    return out
