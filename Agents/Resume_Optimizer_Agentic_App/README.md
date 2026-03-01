<div align="center">

<img src="frontend/assets/qubrid_banner.png" alt="Resume-Optimizer-AI" width="100%">

# Resume-Optimizer-AI 🚀

Transform your resume with AI. Get scored, receive personalized suggestions, and generate ATS-optimized resumes tailored to any job.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📸 UI Screenshots

### 🎯 Upload & Evaluate
<img src="frontend/assets/1-upload.png" alt="Upload Resume" width="1000"/>

*Upload your resume and job description, then get instant AI-powered evaluation with progress tracking.*

---

### 📊 AI Scoring Dashboard
<img src="frontend/assets/2-scoring.png" alt="Resume Evaluation" width="1000"/>

*Receive detailed scores across 4 key metrics: Keyword Optimization, Experience Relevance, ATS-Friendliness, and Professional Formatting.*

---

### 💡 Personalized Suggestions
<img src="frontend/assets/3-suggestions.png" alt="Improvement Suggestions" width="1000"/>

*Get actionable, job-specific recommendations organized by category—review before generating your optimized resume.*

---

### 📄 Optimized Resume Preview
<img src="frontend/assets/4-resume.png" alt="Generated Resume" width="1000"/>

*Preview your AI-tailored resume with all suggestions applied, ready to download as Markdown or PDF.*

---

### 📚 History & Restore
<img src="frontend/assets/5-history.png" alt="Previous Generations" width="600"/>

*Access all past resume generations with scores and iteration counts. Click any chat to restore and review.*

---

### 🌓 Dark Mode Support
<img src="frontend/assets/6-dark-mode.png" alt="Dark Theme" width="1000"/>

*Beautiful dark and light themes with full accessibility and professional color-coded scoring.*

---


## 🏗️ System Architecture

<img src="frontend/assets/architecture.png" alt="System Architecture Diagram" width="1000"/>

*Resume-Optimizer-AI follows a streamlined 5-stage pipeline with persistent storage, ensuring every resume generation is tracked and restorable.*

---

## ✨ Features

- **📊 Instant AI Scoring** - Get 0-10 scores across keyword optimization, ATS compatibility, experience relevance, and formatting
- **💡 Smart Suggestions** - Receive personalized, actionable recommendations before any changes are made
- **🎯 Job-Specific Tailoring** - AI rewrites your resume to match job requirements perfectly
- **📥 Multiple Formats** - Download as Markdown or professional PDF
- **📚 Complete History** - Track and restore all previous resume optimizations
- **🌓 Modern UI** - Sleek dark/light themes with intuitive design
- **⚡ Lightning Fast** - Powered by Mistral 7B via Qubrid API

---

## 🎯 How It Works

1. **Upload** → Add your resume (PDF/Markdown) and job description
2. **Evaluate** → Get instant AI scoring across 4 key metrics
3. **Review** → See personalized improvement suggestions
4. **Generate** → Create your optimized, ATS-friendly resume
5. **Download** → Export as Markdown or PDF

---

## 📊 Scoring Criteria

Your resume is evaluated on:
- **Keyword Optimization** - Job description alignment
- **Experience Relevance** - Skills & role match
- **ATS-Friendliness** - Applicant Tracking System compatibility
- **Professional Formatting** - Structure & readability

Each scored 0-10, averaged for overall score.

---

## 📁 Project Structure

```
resume-optimizer-ai/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── nodes.py              # AI processing functions
│   ├── prompts.py            # AI prompt templates
│   ├── graph.py              # LangGraph workflow
│   ├── database.py           # SQLite operations
│   ├── utils.py              # File processing
│   └── state.py              # Data structure
├── frontend/
│   ├── assets/               # Images, logos
│   │   └── qubrid_logo.png   # Qubrid logo
│   ├── app.py                # Main Streamlit app
│   ├── components.py         # UI components
│   └── styles.py             # CSS themes
├── data/
│   ├── inputs/               # Temporary uploads
│   ├── outputs/              # Generated resumes
│   └── career_sync.db        # SQLite database
├── .env.example              # API key template
├── .gitignore                # Git exclusions
├── pyproject.toml            # Dependencies (single source of truth)
├── test_api.py               # API testing script
└── README.md                 # This file
```

---

## 🛠️ Tech Stack

- **AI**: Mistral 7B via [Qubrid API](https://platform.qubrid.com)
- **Workflow**: LangGraph for orchestration
- **UI**: Streamlit with custom themes
- **Storage**: SQLite for history
- **Processing**: PyPDF2, ReportLab, Markdown

---

## 🎯 Use Cases

✅ **Job Seekers** - Tailor resumes for each application  
✅ **Career Coaches** - Help clients with AI insights  
✅ **Recruiters** - Improve candidate resumes  
✅ **Students** - Build professional resumes  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Qubrid API key](https://platform.qubrid.com)
- UV package manager (recommended)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/aryadoshii/resume-optimizer-ai.git
cd resume-optimizer-ai

# 2. Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # Reload shell (or: source ~/.bashrc)

# 3. Create virtual environment
uv venv

# 4. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR: .venv\Scripts\activate  # Windows

# 5. Install dependencies (recommended)
uv sync  # Uses uv.lock for exact versions
# OR: uv pip install -e .  # Uses pyproject.toml

# 6. Set up API key
cp .env.example .env
nano .env  # Add your QUBRID_API_KEY

# 7. Run the app
streamlit run frontend/app.py
```

---

<div align="center">

  **Made with ❤️ by Qubrid AI**

</div>
