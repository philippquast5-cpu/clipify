#!/usr/bin/env python3
"""Generate opus-clips style ASS subtitles from whisper word timestamps.

Usage: build_ass.py WHISPER.json OUT.ass [STYLE]
STYLE: 'opus' (default), 'karaoke', 'minimal'
"""
import json, sys


def load_json(path):
    """Read JSON written by any shell: handles UTF-8, UTF-8 BOM and UTF-16
    (Windows PowerShell 5.1 writes UTF-16 when you redirect with `>`)."""
    raw = open(path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    return json.loads(text)

WHISPER_JSON = sys.argv[1]
OUT_ASS = sys.argv[2]
STYLE = sys.argv[3] if len(sys.argv) > 3 else "opus"

PLAY_W, PLAY_H = 1080, 1920
# Helvetica ships with macOS only; Arial is the closest font present on Windows/Linux.
SANS_FONT = "Helvetica" if sys.platform == "darwin" else "Arial"

PRESETS = {
    "opus":     dict(font="Arial Black", size=100, chunk=3, highlight="&H0000FFFF&", outline=8, shadow=3),
    "karaoke":  dict(font="Arial Black", size=110, chunk=4, highlight="&H0000FF00&", outline=6, shadow=2),
    "minimal":  dict(font=SANS_FONT,     size=70,  chunk=6, highlight=None,          outline=4, shadow=1),
}
P = PRESETS.get(STYLE, PRESETS["opus"])
WHITE = "&H00FFFFFF&"
OUTLINE = "&H00000000&"

def fmt_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t - h*3600 - m*60
    return f"{h}:{m:02d}:{s:05.2f}"

data = load_json(WHISPER_JSON)
words = []
for seg in data["segments"]:
    for w in seg.get("words", []):
        words.append({"start": w["start"], "end": w["end"], "text": w["word"].strip()})

chunks = [words[i:i+P["chunk"]] for i in range(0, len(words), P["chunk"])]

header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PLAY_W}
PlayResY: {PLAY_H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{P["font"]},{P["size"]},{WHITE},&H000000FF,{OUTLINE},&H00000000,1,0,0,0,100,100,0,0,1,{P["outline"]},{P["shadow"]},2,60,60,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

events = []
for chunk in chunks:
    chunk_end = chunk[-1]["end"]
    for i, w in enumerate(chunk):
        seg_start = w["start"]
        seg_end = chunk[i+1]["start"] if i+1 < len(chunk) else chunk_end
        if seg_end <= seg_start: seg_end = seg_start + 0.05
        if P["highlight"]:
            parts = []
            for j, ww in enumerate(chunk):
                if j == i:
                    parts.append(f"{{\\c{P['highlight']}}}{ww['text']}{{\\c{WHITE}}}")
                else:
                    parts.append(ww["text"])
            line = " ".join(parts)
        else:
            line = " ".join(ww["text"] for ww in chunk)
        events.append(f"Dialogue: 0,{fmt_time(seg_start)},{fmt_time(seg_end)},Default,,0,0,0,,{line}")

with open(OUT_ASS, "w", encoding="utf-8") as f:
    f.write(header + "\n".join(events) + "\n")

print(f"wrote {OUT_ASS}: {len(chunks)} chunks, {len(events)} events", file=sys.stderr)
