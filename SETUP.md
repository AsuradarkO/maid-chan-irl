# Maid-chan IRL — Setup Guide, Part 1: The Laptop Brain
*(Windows 10/11 laptop, 8GB RAM, no GPU. Everything here runs 100% offline —
no API keys, no tokens, no accounts.)*

What you're installing:
| Piece | What it is | RAM while running |
|---|---|---|
| Ollama + `qwen3:4b` | The brain (chat model) | ~3–4 GB |
| Piper TTS (`en_US-amy-medium`) | Her voice | ~0.1–0.4 GB |
| faster-whisper (`base.en`) | Her ears (speech → text) | ~0.3–0.8 GB |
| ffmpeg | Audio conversion glue | negligible |

Windows itself uses ~2.5–3.5 GB, so this is tight but workable. The golden rule:
**never run the brain, ears, and voice all at once** — the bot will pipeline
them one at a time (listen → think → speak).

You need: ~10 GB free disk, Python 3.11+ (`winget install Python.Python.3.11`).

---

## Step 1 — Ollama (the brain's home)

```powershell
winget install Ollama.Ollama
ollama pull qwen3:4b
```

That's a ~2.5–3 GB download. Models live in `%USERPROFILE%\.ollama` — make sure
that drive has room.

## Step 2 — Become Maid-chan

From the folder containing the `Modelfile` (this project folder):

```powershell
ollama create maid-chan -f Modelfile
ollama run maid-chan
```

Say hi. If she greets you like the chatterbox she is, the personality took.
Type `/bye` to exit. If she's slow or rambly, that's Qwen3's "thinking" mode —
the bot script disables it per request (`"think": false`).

RAM getting eaten alive? Fallback: `ollama pull qwen3:1.7b` and change the
Modelfile's first line to `FROM qwen3:1.7b`, then re-run `ollama create`.

## Step 3 — Her voice (Piper TTS)

Fastest offline CPU voice engine out there (~5–9× faster than realtime on
your i7). Easiest Windows route — the frozen binary, no Python needed:

1. Download `piper_windows_amd64.zip` from the piper-tts releases and unzip it
   somewhere, e.g. `C:\maid-chan\piper\`.
2. Download the voice files (each voice = `.onnx` + `.onnx.json` pair) from
   `https://huggingface.co/rhasspy/piper-voices` — our pick:
   `en/en_US/amy/medium/en_US-amy-medium.onnx` (+ the `.onnx.json`).
   (Samples are next to every voice on that page — have a listen first.
   Backups: `en_US-lessac-medium`, `en_GB-jenny_dioco-medium`.)
3. Test it:

```powershell
echo "Ryuunosuke, touch grass!" | .\piper.exe --model en_US-amy-medium.onnx --output_file hello.wav
```

Play `hello.wav`. If it sounds like a cheerful girl nagging a shut-in,
you're golden.

## Step 4 — Her ears (faster-whisper)

```powershell
pip install faster-whisper
python -c "from faster_whisper import WhisperModel; WhisperModel('base.en')"
```

That downloads the ~142 MB English model on first run. On your i7 it
transcribes at ~6–7× realtime — a 10-second voice note takes under 2 seconds.

## Step 5 — ffmpeg (audio glue)

```powershell
winget install Gyan.FFmpeg
```

Needed to convert your phone's voice notes for the ears, and to turn
Piper's WAV output into MP3 voice bubbles the phone can play.

---

## What's next (Part 2)

Vince picked the **unofficial app** — Part 2 is the phone app server + install
guide: [SETUP-PART2.md](SETUP-PART2.md). That's where the Flask server, the
PWA phone UI, and the Tailscale tunnel steps live.

**Maid-chan's notes to future-us:**
- Pipeline order is sacred: transcribe → generate → synthesize. Never overlap
  them or the i7 melts and Windows starts paging.
- The phone records in the browser's native format (usually webm/opus on
  Android Chrome) and uploads it as a Blob — faster-whisper reads it by content,
  so the `.ogg` filename in the upload is just a label, not a requirement.
- The reply audio is served as plain MP3 files under `/api/audio/` — the phone's
  `<audio>` player streams them, no special codec needed.
