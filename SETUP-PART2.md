# Maid-chan IRL — Setup Guide, Part 2: The Unofficial App
*(Finish Part 1 first — the brain, voice, and ears must be installed on the laptop.)*

How it works: your laptop runs a small server; your phone opens it like an app
and "installs" it to the home screen. Tailscale gives your phone a secure
private tunnel to the laptop — free, no router config, and it works on mobile
data, not just home Wi-Fi. No port forwarding, nothing exposed to the internet.

## Step 1 — Tailscale (the private tunnel)

1. On the laptop: install Tailscale from tailscale.com/download (Windows),
   sign in (Google/Microsoft/GitHub — any works), and leave it running.
2. On your Android phone: install the Tailscale app, sign in with the **same
   account**.
3. On the laptop, note its Tailscale IP: open Tailscale → it shows something
   like `100.x.y.z`. That's your laptop's private address.

## Step 2 — The app server

```powershell
pip install flask faster-whisper
cd C:\path\to\maid-chan\app
python server.py
```

You should see: `Maid-chan server on http://0.0.0.0:5000 ...`

If Piper lives somewhere unusual, set these before running:
```powershell
$env:PIPER_BIN   = "C:\maid-chan\piper\piper.exe"
$env:PIPER_VOICE = "C:\maid-chan\piper\en_US-amy-medium.onnx"
$env:FFMPEG_BIN  = "ffmpeg"   # or full path if not on PATH
```

Sanity check on the laptop itself: open `http://localhost:5000` in a browser —
you should see Maid-chan's pink chat UI. Say hi.

## Step 3 — Put her on your phone

1. On your phone (Tailscale connected), open Chrome and go to
   `http://100.x.y.z:5000` — using the Tailscale IP from Step 1.
2. Chrome menu (⋮) → **Add to Home screen** → **Install**. She now lives on
   your home screen like a real app — standalone window, her own icon. 🎀
3. Chat by typing. For voice: tap 🎙️, talk, tap ⏹️ — she'll reply in text
   *and* with a voice bubble you can play.

Windows Firewall may ask about Python on first run — allow it on **private**
networks. (Tailscale counts as private; do NOT tick "public".)

## Living with her — the honest fine print

- **The laptop must be on and awake** for the app to work. She's not in the
  cloud — she's in your room. Set Windows to never sleep while plugged in
  (Settings → System → Power), or she'll doze off with it.
- **First voice note is slow-ish** — the whisper model loads lazily (~a few
  seconds once), then it's ~6–7× realtime after that.
- **RAM:** the server pipelines everything one step at a time
  (listen → think → speak) so your 8GB survives. Don't run a game + Chrome
  with 40 tabs while voice-chatting her.
- **Private by design:** only devices on *your* Tailscale network can reach
  her. Don't share the link publicly.
- **Her memory:** she remembers the last ~20 messages of each conversation.
  Close/reopen the app and she starts fresh — long-term memory is a v2 feature.

## File map

```
maid-chan/
├── personality.md   her personality bible (the canon)
├── Modelfile         bakes the personality into the Ollama model
├── SETUP.md         Part 1 — laptop brain, voice, ears
├── SETUP-PART2.md   Part 2 — this file, the phone app
└── app/
    ├── server.py    the laptop server (chat + voice API)
    └── static/
        ├── index.html    the phone UI
        ├── manifest.json makes it installable
        └── sw.js         offline app shell
```

**Ryuunosuke's code review:** "...it compiles. Ship it."
