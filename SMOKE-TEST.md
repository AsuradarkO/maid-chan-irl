# Maid-chan IRL — 5-minute smoke test
Run these once, in order, after Parts 1 and 2 are installed. If a step fails,
fix it before moving on — each step depends on the one above it.

## 1. The brain
```powershell
ollama list
```
You should see `maid-chan`. Then:
```powershell
ollama run maid-chan
```
Say hi. If she answers like a teasing maid, the personality took.
Type `/bye` to exit. Slow or rambly? That's Qwen3's thinking mode —
the bot disables it per request, so only worry if it's still slow in the app.

## 2. The voice
```powershell
echo "Ryuunosuke, touch grass!" | C:\maid-chan\piper\piper.exe --model en_US-amy-medium.onnx --output_file hello.wav
```
(Adjust the path to wherever you unzipped Piper.) Play `hello.wav` —
if it sounds like a cheerful girl, you're golden.

## 3. The ears
```powershell
python -c "from faster_whisper import WhisperModel; m = WhisperModel('base.en'); print('ears OK')"
```
First run downloads ~142 MB; after that it's instant.

## 4. The app
Start the Flask server, open the PWA on your phone, and try one voice note.
Expected: note uploads → text appears → Maid-chan replies → audio plays back.

## The three most likely failure points
1. **`ollama pull qwen3:4b` crawls or stalls** — it's ~2.5–3 GB. If it keeps
   dying, free disk space first; fallback is `qwen3:1.7b` (see SETUP.md).
2. **RAM pressure** — if Windows starts paging, remember the golden rule:
   never run brain + ears + voice at the same time.
3. **Phone can't reach the server** — Tailscale must be running on BOTH the
   laptop and the phone, on the same account, before the PWA will load.
