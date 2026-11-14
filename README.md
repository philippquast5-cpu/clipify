# Clipify

A [Claude Code](https://claude.com/claude-code) skill that turns long videos into social-ready clips.

![Clipify turns long videos into 9:16 social clips](assets/preview.png)

Point it at any video file and it will:

1. **Find clip-worthy segments** — transcribes the video with [Whisper](https://github.com/openai/whisper) and scans the transcript for punchlines, reversals, awkward pauses, and audio peaks to propose 3–5 candidates.
2. **Create a 9:16 clip** — cuts your chosen moment, then reframes 16:9 → 9:16 with hard-cut pans that follow whoever is speaking (or split-screen if you'd rather see both faces).
3. **Add subtitles** — burns opus-style word-by-word captions (big bold white, yellow active-word highlight).

No cloud APIs. Runs entirely on your machine. No OpenCV. ~20s of work for a 20s clip on Apple Silicon. Works on macOS, Windows and Linux.

## Why this exists

Most "auto-clip" tools are either expensive SaaS, slow, or produce slop. This skill is what I actually use to clip my long-form videos for LinkedIn and TikTok. Built for talking-head dialogue (interviews, podcasts, two-person setups).

## Requirements

- macOS, Windows 10/11 or Linux. `scripts/env.sh` picks the right settings per platform (VideoToolbox decode on macOS, `-hwaccel auto` on Windows, `python` vs `python3`, temp folder).
- [Claude Code](https://claude.com/claude-code)
- `ffmpeg` with `libx264` and `libass`
- [`whisper`](https://github.com/openai/whisper) (`pip install openai-whisper`)
- Python 3 with `numpy` (`pip install numpy`)

## Install

### macOS

```bash
brew install ffmpeg
pip3 install openai-whisper numpy
git clone https://github.com/louisedesadeleer/clipify.git ~/.claude/skills/clipify
```

### Windows

Open **PowerShell** and run:

```powershell
# 1. Tools (skip what you already have). Close and reopen PowerShell afterwards so PATH updates.
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id Gyan.FFmpeg -e

# 2. Python packages
python -m pip install --upgrade pip
python -m pip install openai-whisper numpy

# 3. The skill
git clone https://github.com/louisedesadeleer/clipify.git "$env:USERPROFILE\.claude\skills\clipify"
```

Check it works:

```powershell
ffmpeg -version
python -m whisper --help
```

Notes for Windows:

- Claude Code on Windows runs shell commands through **Git Bash**, which is why Git is required. The skill's commands are written for that shell.
- If `python` opens the Microsoft Store, turn off the `python.exe` / `python3.exe` entries under *Settings → Apps → Advanced app settings → App execution aliases*, then reopen PowerShell.
- Whisper uses PyTorch. The default `pip` install runs on the CPU, which is fine with the `tiny.en` model. For an NVIDIA GPU, install the CUDA build of PyTorch first (see [pytorch.org](https://pytorch.org/get-started/locally/)).
- Clips are written next to your source video in `clipify_out\`; scratch files go to `%LOCALAPPDATA%\Temp\clipify`.

### Linux

```bash
sudo apt install ffmpeg git python3-pip   # or your distro's equivalent
pip3 install openai-whisper numpy
git clone https://github.com/louisedesadeleer/clipify.git ~/.claude/skills/clipify
```

That's it. Restart Claude Code and `/clipify` is available as a slash command.

## Usage

In Claude Code:

```
/clipify
```

Then paste a video file path when asked. The skill will:

1. Transcribe → propose 3–5 funny candidate clips with timestamps and titles
2. Ask which to cut
3. Ask 9:16 / 16:9 / 1:1
4. If 9:16 from 16:9 with two faces: ask pan vs split-screen
5. Ask subtitle style (opus / karaoke / minimal — or paste a reference image to match)
6. Render and open the result

Final clips land in `<source-video-dir>/clipify_out/`.

## How the face-pan works

No face detection model. Camera is static within a single clip, so:

1. Eyeball each face's mouth+chin area as a rectangle on one sample frame.
2. ffmpeg computes per-frame motion energy in each rectangle using frame differencing.
3. Whichever rectangle has more motion at a given moment = that's the speaker.
4. Build a hard-cut x-coordinate expression from the speaker timeline.
5. Crop a vertical strip from the source that follows whoever's talking.

Total cost: a few seconds of ffmpeg per clip. Works surprisingly well.

## Repo structure

```
clipify/
├── SKILL.md           # the skill prompt Claude Code reads
├── scripts/
│   ├── analyze.py     # speaker timeline from two ROI motion files
│   ├── build_pan.py   # ffmpeg crop x-expression with hard cuts
│   ├── build_ass.py   # opus/karaoke/minimal ASS captions from whisper JSON
│   ├── audio_align.py # find offset of a sub-clip in a longer source
│   ├── detect_transients.py # find impact sounds for action montages
│   └── env.sh         # per-platform setup (macOS / Windows / Linux)
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).

Built by [Louise de Sadeleer](https://github.com/louisedesadeleer), Growth at [Tella](https://tella.tv).
