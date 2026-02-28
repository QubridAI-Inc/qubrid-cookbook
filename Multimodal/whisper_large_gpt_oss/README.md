<div align="center">

<img src="frontend/assets/qubrid_banner.png" alt="AudioSnap AI" width="100%">

# AudioSnap AI

**Turn any audio into instant intelligence.**  
Chapters · Key Moments · Full Transcript - in seconds.

<br>

![Python](https://img.shields.io/badge/Python-3.10+-14b8a6?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-14b8a6?style=flat-square&logo=streamlit&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper--v3-OpenAI-0891b2?style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-0d9488?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-475569?style=flat-square)

</div>

## What it does

AudioSnap AI takes any audio — a podcast clip, YouTube video, meeting recording, or voice note — and returns structured intelligence within seconds:

- **Smart Chapters** with timestamps and summaries
- **Key Moments** — the most quotable, shareable clips
- **Full Transcript** with search and CSV export
- **Topic Map** showing which themes appear across chapters
- **AI Confidence Score** — the model rates its own output

Powered by **Whisper-v3** for transcription and **GPT-OSS-120B** for analysis, running on [Qubrid AI](https://qubrid.com) infrastructure.

---

## Screenshots


🏠 Interface
<div align="center">
<img src="frontend/assets/home-collapsed.png" alt="Clean Interface" width="100%">
<sub>Clean, focused interface with collapsed sidebar</sub>
<br><br>
<img src="frontend/assets/home-sidebar.png" alt="Sidebar with History" width="100%">
<sub>Session history sidebar with one-click recall</sub>
 <br><br>
<img src="frontend/assets/mode-selector.png" alt="Mode Selector" width="100%">
<sub>Three input modes — Upload File · YouTube URL · Record Live</sub>
<br>
<sub>🎙 Podcast Clips &nbsp;·&nbsp; 📹 YouTube Videos &nbsp;·&nbsp; 💼 Meetings &nbsp;·&nbsp; 🎤 Interviews &nbsp;·&nbsp; 📱 Shorts & Reels &nbsp;·&nbsp; 🗣 Voice Notes</sub>
</div>

---

🎙 Podcast
<div align="center">
<img src="frontend/assets/pod-chapters.png" alt="Podcast Chapters" width="100%">
<sub>Smart chapters with timestamps — automatically grouped by topic</sub>
<br><br>
<img src="frontend/assets/pod-keymoments.png" alt="Key Moments" width="100%">
<sub>Key moments extracted as quotable cards — ready to clip and share</sub>
<br><br>
<img src="frontend/assets/pod-transcript.png" alt="Full Transcript" width="100%">
<sub>Full searchable transcript with timestamps and one-click CSV export</sub>
<br><br>
<img src="frontend/assets/pod-topics.png" alt="Topic Map" width="100%">
<sub>Topic map — themes cross-referenced across chapters</sub>
</div>

---

▶️ YouTube URL Analysis
<div align="center">
<img src="frontend/assets/yt-home.png" alt="YouTube Input" width="100%">
<sub>Paste any YouTube link — thumbnail previews instantly</sub>
<br><br>
<img src="frontend/assets/yt-analyzing.png" alt="Analyzing" width="100%">
<sub>Downloading audio + running Whisper-v3 transcription and GPT-OSS-120B analysis</sub>
<br><br>
<img src="frontend/assets/yt-chapters.png" alt="Chapters" width="100%">
<sub>Smart chapters with timestamps and summaries generated automatically</sub>
<br><br>
<img src="frontend/assets/yt-transcript.png" alt="Transcript" width="100%">
<sub>Full searchable transcript with timestamps and CSV export</sub>
</div>

---

🔴 Live Recording
<div align="center">
<img src="frontend/assets/live-permission.png" alt="Mic Permission" width="100%">
<sub>Browser mic permission prompt — records directly in the browser, no installs needed</sub>
<br><br>
<img src="frontend/assets/live-recording.png" alt="Recording with Waveform" width="100%">
<sub>Live waveform visualizer while recording — hit Analyze when done</sub>
<br><br>
<img src="frontend/assets/live-chapters.png" alt="Live Chapters" width="100%">
<sub>Chapters generated from live audio — same full analysis as uploaded files</sub>
<br><br>
<img src="frontend/assets/live-transcript.png" alt="Live Transcript" width="100%">
<sub>Timestamped transcript from browser mic audio</sub>
</div>

---

## Architecture


<img src="frontend/assets/architecture.png" alt="System Architecture Diagram" width="500"/>


---

## Input Modes

| Mode | Description | Limit |
|------|-------------|-------|
| **Upload File** | MP3, WAV, M4A | 200 MB |
| **YouTube URL** | Any public video | First 12 min |
| **Record Live** | Browser microphone | Session length |

---

## Project Structure

```
audio-snap-ai/
├── app.py                    # Streamlit entry point
├── frontend/
│   ├── components.py         # Hero, mode selector, results UI
│   ├── sidebar.py            # History sidebar
│   ├── styles.py             # All CSS + JS injections
│   └── views.py              # Layout orchestration
├── backend/
│   ├── graph.py              # LangGraph agentic pipeline
│   ├── nodes.py              # Individual agent nodes
│   └── database.py           # SQLite history store
├── config/
│   └── settings.py           # Environment config
├── assets/
│   ├── screenshots/          # UI screenshots
│   └── qubrid_logo.png       # Logo (+ add banner.png here)
├── .env.example
└── pyproject.toml
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit + custom CSS/JS |
| Transcription | Whisper-v3 via Qubrid API |
| Intelligence | GPT-OSS-120B via Qubrid API |
| Orchestration | LangGraph |
| YouTube | yt-dlp |
| History | SQLite |

---


## Getting Started

### Prerequisites

- Python 3.10+
- A [Qubrid AI](https://qubrid.com) API key
- `ffmpeg` installed (for YouTube audio processing)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/aryadoshii/audio-snap-ai.git
cd audio-snap-ai

# 2. Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # Reload shell (or: source ~/.bashrc)

# 3. Create virtual environment
uv venv

# 4. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR: .venv\Scripts\activate  # Windows

# 5. Install dependencies
uv sync  # Uses uv.lock for exact versions
# OR: uv pip install -e .  # Uses pyproject.toml

# 6. Set up API key
cp .env.example .env
nano .env  # Add your QUBRID_API_KEY

# 7. Run the app
streamlit run app.py
```

### Environment Variables

```env
QUBRID_API_KEY=your_api_key_here
QUBRID_BASE_URL=https://api.qubrid.com/v1
```
---


<div align="center">

  **Made with ❤️ by Qubrid AI**

</div>
