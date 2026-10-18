#!/usr/bin/env python3
"""
Maid-chan IRL — unofficial app server.
Runs on the laptop. Serves the phone UI and the chat/voice API.

  pip install flask faster-whisper
  python server.py

Environment overrides:
  OLLAMA_URL      (default http://localhost:11434)
  MAIDCHAN_MODEL  (default maid-chan)
  PIPER_BIN       (default C:\\maid-chan\\piper\\piper.exe)
  PIPER_VOICE     (default C:\\maid-chan\\piper\\en_US-amy-medium.onnx)
  FFMPEG_BIN      (default ffmpeg, must be on PATH)
  WHISPER_MODEL   (default base.en)
  MAIDCHAN_PORT   (default 5000)

Pipeline per voice note (strictly sequential — 8GB RAM is sacred):
  transcribe (whisper) -> generate (ollama) -> synthesize (piper) -> mp3 (ffmpeg)
"""

import json
import os
import re
import subprocess
import tempfile
import urllib.request
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE = Path(__file__).resolve().parent
AUDIO_DIR = BASE / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("MAIDCHAN_MODEL", "maid-chan")
PIPER_BIN = os.environ.get("PIPER_BIN", r"C:\maid-chan\piper\piper.exe")
PIPER_VOICE = os.environ.get("PIPER_VOICE", r"C:\maid-chan\piper\en_US-amy-medium.onnx")
FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base.en")
PORT = int(os.environ.get("MAIDCHAN_PORT", "5000"))

# Only serve back files we created: 32-hex-char names ending in .mp3
SAFE_AUDIO = re.compile(r"^[0-9a-f]{32}\.mp3$")

app = Flask(__name__, static_folder=str(BASE / "static"), static_url_path="/static")

_whisper = None


def get_whisper():
    """Lazy-load the STT model so idle RAM stays low."""
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel

        _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _whisper


def ollama_chat(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,  # Qwen3 thinking mode off: snappy chat replies
        "options": {"num_predict": 512},
    }
    req = urllib.request.Request(
        OLLAMA_URL + "/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())["message"]["content"]
    except Exception as e:  # Ollama down, model missing, etc.
        raise RuntimeError(f"Couldn't reach the brain ({OLLAMA_URL}): {e}")


def speak(text):
    """Piper TTS -> WAV -> MP3. Returns the audio filename."""
    tag = uuid.uuid4().hex
    wav = AUDIO_DIR / f"{tag}.wav"
    mp3 = AUDIO_DIR / f"{tag}.mp3"
    subprocess.run(
        [PIPER_BIN, "--model", PIPER_VOICE, "--output_file", str(wav)],
        input=text.encode("utf-8"),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", str(wav),
         "-codec:a", "libmp3lame", "-q:a", "4", str(mp3)],
        check=True,
        capture_output=True,
    )
    wav.unlink(missing_ok=True)
    return mp3.name


@app.get("/")
def index():
    return send_from_directory(BASE / "static", "index.html")


@app.post("/api/chat")
def api_chat():
    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages sent."}), 400
    try:
        reply = ollama_chat(messages)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    return jsonify({"reply": reply})


@app.post("/api/voice")
def api_voice():
    """Accept a voice note, return transcript + text reply + spoken reply."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio uploaded."}), 400
    tmp = Path(tempfile.gettempdir()) / f"maid_in_{uuid.uuid4().hex}.ogg"
    request.files["audio"].save(tmp)
    try:
        # 1. Ears
        try:
            segments, _ = get_whisper().transcribe(str(tmp))
        except Exception as e:
            return jsonify({"error": f"Ears failed (whisper): {e}"}), 500
        transcript = " ".join(s.text for s in segments).strip()
        if not transcript:
            return jsonify({"error": "Couldn't hear anything in that note."}), 400

        # 2. Brain
        history = json.loads(request.form.get("messages", "[]"))
        history.append({"role": "user", "content": transcript})
        try:
            reply = ollama_chat(history)
        except RuntimeError as e:
            return jsonify({"transcript": transcript, "error": str(e)}), 502

        # 3. Voice
        try:
            audio_name = speak(reply)
        except Exception as e:
            # Text reply still works even if TTS breaks
            return jsonify({"transcript": transcript, "reply": reply,
                            "error": f"Voice box failed: {e}"}), 200

        return jsonify({"transcript": transcript, "reply": reply,
                        "audio": f"/api/audio/{audio_name}"})
    finally:
        tmp.unlink(missing_ok=True)


@app.get("/api/audio/<name>")
def api_audio(name):
    if not SAFE_AUDIO.match(name):
        return jsonify({"error": "Nope."}), 404
    return send_from_directory(AUDIO_DIR, name, mimetype="audio/mpeg")


if __name__ == "__main__":
    print(f"Maid-chan server on http://0.0.0.0:{PORT}  (brain: {OLLAMA_URL}, model: {MODEL})")
    app.run(host="0.0.0.0", port=PORT, threaded=True)
