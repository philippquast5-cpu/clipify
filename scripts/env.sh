# Clipify platform setup. Source this at the start of every shell command:
#   source <skill-dir>/scripts/env.sh
# Shell variables don't persist between Claude Code tool calls, so re-source it each time.
# It sets: PY (python interpreter), WHISPER (whisper CLI), HWACCEL (ffmpeg decode flag),
#          WORK (scratch dir), OPEN (command that opens a file), and cd's into $WORK.
# On Windows, Claude Code's Bash tool runs Git Bash, so this file works there too.

case "$(uname -s)" in
  Darwin)
    PY=python3
    HWACCEL="-hwaccel videotoolbox"
    WORK="/tmp/clipify"
    OPEN="open"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    # Windows (Git Bash). "python3" is often only the Microsoft Store stub, so use "python".
    PY=python
    # Let ffmpeg pick D3D11VA/DXVA2/CUDA/QSV if available, otherwise it decodes in software.
    HWACCEL="-hwaccel auto"
    # Use a C:/... style path (forward slashes) so native Windows tools understand it.
    WORK="$(cygpath -m "${LOCALAPPDATA:-$USERPROFILE/AppData/Local}")/Temp/clipify"
    OPEN="start"
    ;;
  *)
    PY=python3
    HWACCEL=""
    WORK="/tmp/clipify"
    OPEN="xdg-open"
    ;;
esac

# pip on Windows often installs whisper.exe into a Scripts folder that isn't on PATH.
if command -v whisper >/dev/null 2>&1; then
  WHISPER="whisper"
else
  WHISPER="$PY -m whisper"
fi

# Python on Windows defaults to a legacy code page; force UTF-8 for script I/O.
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

mkdir -p "$WORK" && cd "$WORK" || return 1
