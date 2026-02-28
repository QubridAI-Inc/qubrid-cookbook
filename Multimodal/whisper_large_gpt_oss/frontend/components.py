import streamlit as st
import pandas as pd
import os
import re as _re
from config.settings import config
from backend.graph import app_graph
from backend.database import save_result


def render_hero():
    st.markdown("""
    <div class="hero-wrap">
        <h1 class="hero-title">AudioSnap AI</h1>
        <p class="hero-tagline">
            World-class transcription by <span class="tagline-highlight">Whisper-v3</span>,
            instant intelligence from <span class="tagline-dim">GPT-OSS-120B</span>
        </p>
        <p class="hero-subtitle">
            Turn any audio into instant intelligence —
            chapters, key moments, and a full transcript in seconds.
        </p>
        <div class="hero-pills">
            <span class="hero-pill">🎙 Podcast Clips</span>
            <span class="hero-pill">📹 YouTube Videos</span>
            <span class="hero-pill">💼 Meetings</span>
            <span class="hero-pill">🎤 Interviews</span>
            <span class="hero-pill">📱 Shorts &amp; Reels</span>
            <span class="hero-pill">🗣 Voice Notes</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_input_mode_selector():
    if "input_mode" not in st.session_state:
        st.session_state["input_mode"] = "upload"

    st.markdown('<p style="text-align:center;font-size:0.7rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#334155;margin-bottom:10px;">Choose your source</p>', unsafe_allow_html=True)

    modes = [
        ("upload",  "📁", "Upload File",  "MP3 · WAV · M4A"),
        ("youtube", "▶️",  "YouTube URL",  "Any video link"),
        ("record",  "🎙", "Record Live",  "Browser mic"),
    ]

    # Row 1: pure HTML cards only
    col1, col2, col3 = st.columns(3, gap="small")
    for col, (mode_id, icon, label, sub) in zip([col1,col2,col3], modes):
        active = st.session_state["input_mode"] == mode_id
        border = "2px solid rgba(20,184,166,0.7)" if active else "1px solid rgba(255,255,255,0.07)"
        bg     = "rgba(20,184,166,0.12)" if active else "rgba(255,255,255,0.025)"
        lc     = "#5eead4" if active else "#94a3b8"
        sc     = "#14b8a6" if active else "#334155"
        dot    = '<div class="active-dot"></div>' if active else ""
        with col:
            st.markdown(
                f'<div class="mode-card" style="background:{bg};border:{border};">'
                f'<div style="font-size:1.6rem;margin-bottom:6px;">{icon}</div>'
                f'<div style="font-size:0.85rem;font-weight:700;color:{lc};">{label}</div>'
                f'<div style="font-size:0.7rem;color:{sc};margin-top:3px;">{sub}</div>'
                f'{dot}</div>', unsafe_allow_html=True
            )

    # Row 2: invisible buttons (hidden by CSS .mode-btn-row)
    st.markdown('<div class="mode-btn-row">', unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3, gap="small")
    clicked = None
    with b1:
        if st.button("Upload File",  key="mode_upload",  use_container_width=True): clicked = "upload"
    with b2:
        if st.button("YouTube URL",  key="mode_youtube", use_container_width=True): clicked = "youtube"
    with b3:
        if st.button("Record Live",  key="mode_record",  use_container_width=True): clicked = "record"
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        st.session_state["input_mode"] = clicked
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


def render_upload_input():
    with st.container(border=True):
        uploaded_file = st.file_uploader("Drop your audio file here", type=["mp3","wav","m4a"])
        if uploaded_file:
            save_path = config.INPUT_DIR / uploaded_file.name
            save_path.write_bytes(uploaded_file.getbuffer())
            st.audio(uploaded_file)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✨ Analyze Audio", use_container_width=True, type="primary"):
                _run_analysis(str(save_path), uploaded_file.name)


def render_youtube_input():
    st.markdown("""
    <div style="background:rgba(255,60,60,0.06);border:1px solid rgba(255,80,80,0.2);
                border-radius:14px;padding:16px 20px;margin-bottom:16px;">
        <div style="font-size:0.75rem;font-weight:700;color:#f87171;letter-spacing:0.08em;margin-bottom:5px;">
            ▶ YOUTUBE ANALYZER
        </div>
        <div style="font-size:0.85rem;color:#94a3b8;line-height:1.6;">
            Paste any YouTube link. We download the first
            <strong style="color:#e2e8f0;">12 minutes</strong> and run full AI analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", key="yt_url", label_visibility="collapsed")
    if url and url.strip():
        video_id = _extract_yt_id(url.strip())
        if video_id:
            st.markdown(f'<div style="text-align:center;margin:12px 0;"><img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" style="border-radius:12px;max-width:360px;width:100%;border:1px solid rgba(255,255,255,0.1);box-shadow:0 8px 32px rgba(0,0,0,0.4);"></div>', unsafe_allow_html=True)
        if st.button("Analyze Video", use_container_width=True, type="primary"):
            with st.spinner("Downloading audio from YouTube…"):
                audio_path, title, error = _download_youtube(url.strip())
            if error:
                st.error(f"Download failed: {error}")
            else:
                st.success(f"✓ Downloaded: {title}")
                _run_analysis(audio_path, title + ".mp3")


def _extract_yt_id(url):
    m = _re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else ""

def _download_youtube(url):
    import yt_dlp
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(config.INPUT_DIR / "yt_audio.%(ext)s"),
            "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"128"}],
            "download_sections": [{"*": "0:00-12:00"}],
            "noplaylist": True, "quiet": True,
            "no_warnings": True,
            "extractor_args": {"youtube": {"js_runtimes": ["deno"]}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "YouTube Audio")
        return str(config.INPUT_DIR / "yt_audio.mp3"), title, ""
    except Exception as e:
        return "", "", str(e)


def render_record_input():
    st.markdown("""
    <div style="background:rgba(20,184,166,0.06);border:1px solid rgba(20,184,166,0.2);
                border-radius:14px;padding:16px 20px;margin-bottom:16px;">
        <div style="font-size:0.75rem;font-weight:700;color:#5eead4;letter-spacing:0.08em;margin-bottom:5px;">🎙 LIVE RECORDING</div>
        <div style="font-size:0.85rem;color:#94a3b8;line-height:1.6;">
            Record directly in your browser — perfect for <strong style="color:#e2e8f0;">meetings, interviews, or voice notes.</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    audio_bytes = st.audio_input("Record audio")
    if audio_bytes:
        save_path = config.INPUT_DIR / "recording.wav"
        save_path.write_bytes(audio_bytes.getvalue())
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ Analyze Recording", use_container_width=True, type="primary"):
            _run_analysis(str(save_path), "recording.wav")


def _run_analysis(audio_path, filename):
    with st.spinner("Transcribing with Whisper-v3 · Analyzing with GPT-OSS-120B…"):
        result = app_graph.invoke({"audio_path": audio_path})
    if "Error" in result.get("status", ""):
        st.error(result["status"])
    else:
        save_result(filename, result)
        st.session_state.update({"active_view":"result","result":result,"filename":filename,"audio_path":audio_path})
        st.rerun()


def render_uploader():
    render_input_mode_selector()
    mode = st.session_state.get("input_mode", "upload")
    if mode == "upload":    render_upload_input()
    elif mode == "youtube": render_youtube_input()
    elif mode == "record":  render_record_input()


def render_results(result=None, filename=None, audio_path=None):
    result     = result     or st.session_state.get("result", {})
    filename   = filename   or st.session_state.get("filename", "transcript")
    audio_path = audio_path or st.session_state.get("audio_path")
    chapters   = result.get("chapters", [])
    brief      = result.get("episode_brief", "")
    moments    = result.get("key_moments", [])
    segments   = result.get("transcript_segments", [])
    topics     = result.get("topics", [])
    confidence = result.get("confidence_scores", {})

    if brief:
        st.markdown(
            f'<div class="brief-card">'
            f'<div class="brief-label">📋 Summary</div>'
            f'<div class="brief-text">{brief}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if audio_path and os.path.exists(audio_path):
        st.audio(audio_path)

    st.markdown("<hr>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Chapters", "✨ Key Moments", "🔍 Transcript", "🗺️ Topics"])

    with tab1:
        if chapters:
            for i, ch in enumerate(chapters):
                st.markdown(f'<div class="chapter-card"><div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;"><span style="font-size:0.68rem;font-weight:800;color:#14b8a6;background:rgba(255,255,255,0.05);padding:2px 7px;border-radius:4px;">#{i+1:02d}</span><span class="chapter-timestamp">{ch["timestamp"]}</span><span class="chapter-title">{ch["title"]}</span></div><div class="chapter-summary">{ch.get("summary","")}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No chapters generated.")

    with tab2:
        if moments:
            st.markdown('<p style="font-size:0.78rem;color:#475569;margin-bottom:20px;">The most quotable moments — worth clipping and sharing.</p>', unsafe_allow_html=True)
            for m in moments:
                st.markdown(f'<div class="quote-card"><div class="quote-mark">&ldquo;</div><div class="quote-text">{m.get("quote","")}</div><div class="quote-footer"><span class="chapter-timestamp">{m.get("timestamp","")}</span><span class="quote-reason">{m.get("reason","")}</span></div></div>', unsafe_allow_html=True)
        else:
            st.info("No key moments found.")

    with tab3:
        query  = st.text_input("Search transcript", placeholder="🔍  Search the transcript…", label_visibility="collapsed")
        df_all = pd.DataFrame(segments)[["timestamp","text"]] if segments else pd.DataFrame()
        def _highlight(text, q):
            return _re.sub(f"({_re.escape(q)})", r'<mark style="background:rgba(20,184,166,0.35);color:#ccfbf1;border-radius:3px;padding:0 2px;">\1</mark>', text, flags=_re.IGNORECASE)
        def _row(ts, text, q=""):
            body = _highlight(text, q) if q else text
            st.markdown(f'<div style="display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);"><span class="chapter-timestamp" style="flex-shrink:0;margin-top:2px;">{ts}</span><span style="color:#94a3b8;font-size:0.88rem;line-height:1.65;">{body}</span></div>', unsafe_allow_html=True)
        if not df_all.empty:
            if query:
                res = df_all[df_all["text"].str.contains(query, case=False, na=False)]
                st.markdown(f'<div class="match-badge">{len(res)} match{"es" if len(res)!=1 else ""} across {len(df_all)} segments</div>', unsafe_allow_html=True)
                for _, row in res.iterrows(): _row(row["timestamp"], row["text"], query)
            else:
                P = 20
                st.markdown(f'<div style="font-size:0.75rem;color:#475569;margin-bottom:12px;">Showing first {min(P,len(df_all))} of {len(df_all)} segments</div>', unsafe_allow_html=True)
                for _, row in df_all.head(P).iterrows(): _row(row["timestamp"], row["text"])
                if len(df_all) > P:
                    st.markdown(f'<div style="text-align:center;padding:12px;margin-top:8px;background:rgba(20,184,166,0.06);border:1px dashed rgba(20,184,166,0.25);border-radius:10px;color:#5eead4;font-size:0.82rem;">+ {len(df_all)-P} more — download CSV below</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Full Transcript (CSV)", df_all.to_csv(index=False), f"{filename}_transcript.csv", "text/csv")

    with tab4:
        if topics:
            for t in topics:
                chap_list = ", ".join(t.get("chapters",[])) if isinstance(t.get("chapters"),list) else str(t.get("chapters",""))
                st.markdown(f'<div class="topic-card"><div class="topic-name">{t.get("topic","")}</div><div class="topic-chapters">Appears in: {chap_list}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No topics mapped.")
