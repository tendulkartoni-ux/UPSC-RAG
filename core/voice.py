"""
Voice I/O.

INPUT: Browser Web Speech API (free, runs client-side in Chrome/Edge). No server-side
       STT needed — this is why the app works with zero extra infrastructure.

OUTPUT: gTTS (Google Translate TTS — free, no key). Falls back to browser speech
        synthesis if gTTS fails.

Both options keep the app deployable on free Streamlit Cloud with no extra services.
"""
from __future__ import annotations
import base64
import io
import streamlit as st
import streamlit.components.v1 as components


# ── Text → Speech (gTTS) ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, max_entries=32)
def synthesize_speech(text: str, lang: str = "en", slow: bool = False) -> bytes:
    """Generate MP3 bytes from text. Cached so re-plays are instant."""
    try:
        from gtts import gTTS
        # Clip to gTTS-friendly length (huge texts fail)
        if len(text) > 4500:
            text = text[:4500] + "…"
        tts = gTTS(text=text, lang=lang, slow=slow)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return b""


def play_audio(text: str, autoplay: bool = False, lang: str = "en"):
    """Render an audio element that plays the given text."""
    if not text.strip():
        return
    mp3 = synthesize_speech(text, lang=lang)
    if not mp3:
        # Fallback — browser speech synthesis
        _browser_tts_fallback(text, autoplay=autoplay)
        return
    b64 = base64.b64encode(mp3).decode()
    autoplay_attr = "autoplay" if autoplay else ""
    html = f"""
    <audio controls {autoplay_attr} style="width:100%; margin-top:4px;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)


def _browser_tts_fallback(text: str, autoplay: bool = False):
    """Use the browser's built-in speech synthesis API as a last resort."""
    safe = text.replace("`", "'").replace("\\", "").replace("\n", " ")
    # Escape quotes for JS string
    safe = safe.replace('"', '\\"')
    auto = "window.speechSynthesis.speak(u);" if autoplay else ""
    components.html(f"""
    <div style="padding:8px;background:#faf7f2;border-radius:8px;">
      <button onclick='var u=new SpeechSynthesisUtterance("{safe}");u.rate=0.95;window.speechSynthesis.speak(u);'
              style="padding:6px 14px;border:1px solid #8b6f47;border-radius:6px;
                     background:#fff;color:#3d2817;cursor:pointer;font-family:inherit;">
        🔊 Play (browser voice)
      </button>
    </div>
    <script>{auto}</script>
    """, height=55)


# ── Speech → Text (Browser Web Speech API component) ─────────────────────────
def voice_input_component(key: str = "voice_input", height: int = 140) -> str | None:
    """
    Renders a mic button + transcript display. The transcript is sent back via
    Streamlit's `setComponentValue`. Returns the transcript (or None).

    Note: Works in Chrome/Edge/Safari. Firefox does NOT support Web Speech API yet.
    """
    html = """
    <style>
      .sansad-mic-wrap {
        font-family: 'Georgia', 'Libre Baskerville', serif;
        background: linear-gradient(135deg, #faf7f2 0%, #f5efe4 100%);
        border: 1px solid #d9c9a8;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
      }
      .sansad-mic-btn {
        width: 72px; height: 72px;
        border-radius: 50%;
        border: none;
        background: linear-gradient(145deg, #8b6f47, #6b4e2a);
        color: #faf7f2;
        font-size: 28px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(107, 78, 42, 0.3);
        transition: transform .15s, box-shadow .15s;
      }
      .sansad-mic-btn:hover { transform: scale(1.05); }
      .sansad-mic-btn.recording {
        background: linear-gradient(145deg, #c73e3a, #8a2622);
        animation: pulse 1.2s infinite;
      }
      @keyframes pulse {
        0%,100% { box-shadow: 0 4px 12px rgba(199, 62, 58, .5); }
        50%     { box-shadow: 0 4px 28px rgba(199, 62, 58, .9); }
      }
      .sansad-mic-hint { color: #6b4e2a; font-size: 13px; margin-top:10px; font-style: italic; }
      .sansad-mic-text {
        margin-top: 14px; padding: 12px; min-height: 40px;
        background: #fff; border: 1px dashed #c9b68f; border-radius: 8px;
        color: #3d2817; text-align: left; font-size: 15px;
      }
      .sansad-mic-text:empty::before { content: "Your speech will appear here…"; color: #a8926b; }
    </style>
    <div class="sansad-mic-wrap">
      <button id="micBtn" class="sansad-mic-btn" onclick="toggleMic()">🎤</button>
      <div class="sansad-mic-hint" id="micHint">Click and speak — release when done</div>
      <div class="sansad-mic-text" id="micText"></div>
      <button id="submitBtn" onclick="submitText()"
              style="margin-top:10px;padding:8px 18px;border:none;border-radius:6px;
                     background:#6b4e2a;color:#faf7f2;cursor:pointer;display:none;">
        ✓ Use this
      </button>
    </div>
    <script>
      let recognition = null;
      let isRecording = false;
      let finalTranscript = "";

      function setup() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
          document.getElementById('micHint').innerHTML =
            "⚠️ Voice input isn't supported in this browser. Try Chrome, Edge, or Safari.";
          document.getElementById('micBtn').disabled = true;
          return;
        }
        recognition = new SR();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-IN';

        recognition.onresult = (e) => {
          let interim = "";
          for (let i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) {
              finalTranscript += e.results[i][0].transcript + " ";
            } else {
              interim += e.results[i][0].transcript;
            }
          }
          document.getElementById('micText').innerText = finalTranscript + interim;
          if (finalTranscript.trim()) {
            document.getElementById('submitBtn').style.display = 'inline-block';
          }
        };
        recognition.onerror = (e) => {
          document.getElementById('micHint').innerText = "Error: " + e.error;
          stopRec();
        };
        recognition.onend = () => { if (isRecording) recognition.start(); };
      }

      function toggleMic() {
        if (!recognition) return;
        if (isRecording) { stopRec(); }
        else { startRec(); }
      }
      function startRec() {
        finalTranscript = "";
        document.getElementById('micText').innerText = "";
        document.getElementById('submitBtn').style.display = 'none';
        document.getElementById('micBtn').classList.add('recording');
        document.getElementById('micHint').innerText = "Listening… click mic to stop";
        isRecording = true;
        recognition.start();
      }
      function stopRec() {
        isRecording = false;
        try { recognition.stop(); } catch(e) {}
        document.getElementById('micBtn').classList.remove('recording');
        document.getElementById('micHint').innerText = "Click and speak — release when done";
      }
      function submitText() {
        const t = document.getElementById('micText').innerText.trim();
        if (!t) return;
        window.parent.postMessage({
          isStreamlitMessage: true,
          type: 'streamlit:setComponentValue',
          value: t
        }, '*');
        // visual feedback
        document.getElementById('submitBtn').innerText = '✓ Sent — processing…';
        document.getElementById('submitBtn').disabled = true;
      }
      setup();
    </script>
    """
    return components.html(html, height=height)
