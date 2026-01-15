<div align="center">

![Qubrid AI Banner](docs/screenshots/qubrid_banner.png)

---

# 🔧 DiagnostiQ

### 🏭 **Industrial Component Diagnostics** 🔍

<sub>*⚡ A production-ready INDUSTRIAL COMPONENT DIAGNOSTICS CHATBOT powered by Qubrid AI's advanced vision model Qwen3-VL-30B-A3B-Instruct ⚡*</sub>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.29+-red.svg?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-Qwen3--VL--30B-green.svg?style=for-the-badge&logo=openai&logoColor=white" alt="AI Model">
  <img src="https://img.shields.io/badge/Platform-Qubrid_AI-purple.svg?style=for-the-badge&logo=github&logoColor=white" alt="Platform">
</p>

<p align="center">
  <strong>🎯 Defect Detection</strong> • 
  <strong>⚠️ Safety Auditing</strong> • 
  <strong>📊 Technical Analysis</strong> • 
  <strong>📄 PDF Reports</strong>
</p>

</div>

---

## 🎯 Overview

### The Problem

In industrial manufacturing and maintenance environments, **visual inspection of equipment and components is critical but challenging**. Quality control engineers and safety officers spend countless hours manually examining machinery parts, PCBs, welds, and mechanical assemblies to identify defects, wear patterns, and safety hazards. This process is:

- ⏰ **Time-Consuming:** Manual inspection of hundreds of components daily
- 👁️ **Inconsistent:** Human fatigue leads to missed defects
- 📋 **Poorly Documented:** Handwritten notes and informal reports
- 💰 **Costly:** Defects caught late in production cause expensive rework
- ⚠️ **Safety-Critical:** Missed cracks or corrosion can lead to equipment failure

Traditional computer vision systems require extensive training data, complex setup, and lack the flexibility to analyze diverse industrial components with natural language interaction.

### The Solution

**DiagnostiQ** is a vision-based quality control assistant that transforms how industrial teams inspect and diagnose equipment. By leveraging **Multimodal Large Language Models (LLMs)** via the **Qubrid AI platform**, it enables operators to simply upload a photo and ask questions in plain English—receiving instant, detailed technical analysis.

Unlike generic AI tools, DiagnostiQ is **calibrated specifically for industrial environments**. It features intelligent guardrails to reject non-technical inputs (e.g., food, pets) while maintaining high sensitivity for valid industrial defects like micro-fractures in silicon dies or rust on pipe fittings.

### 🚀 Key Capabilities

- 🔍 **Defect Detection:** Identifies cracks, corrosion, thermal damage, and PCB faults with severity classification
- ⚠️ **Safety Auditing:** Flags OSHA/HSE hazards including exposed wiring, structural damage, and PPE requirements
- 📊 **Technical Analysis:** Extracts component specifications, material identification, and operational context
- 📄 **Automated Reporting:** Generates downloadable PDF maintenance reports with conversation history and metrics
- 💬 **Conversational Interface:** Natural language interaction—no specialized training required

---

## ✨ Features & Engineering

### 1. Intelligent Analysis Protocols

We implemented three distinct "Personas" that change the AI's behavior and output format:

- **General Analysis:** Acts as a Senior Engineer. Outputs specs, material ID, and function.
- **Defect Inspection:** Acts as a Forensic Analyst. Outputs a **Markdown QA Table** listing specific anomalies, severity scores (Critical/Major), and rejection criteria.
- **Safety Audit:** Acts as an HSE Officer. Outputs a **Hazard Matrix** identifying risks and required PPE.

### 2. Robust Session Management (SQLite)

- **Persistent History:** All chats, images, and metadata are stored in a local SQLite database (`diagnostiq.db`).
- **"Ghost" Handling:** Automatically cleans up empty "New Inspection" sessions to keep the history clean.
- **State Memory:** The app remembers which protocol (e.g., Defect Mode) was used for a specific chat, even after restarting.
- **CRUD Operations:** Users can **Rename** sessions for organization or **Delete** them to free up disk space (auto-deletes associated images).

### 3. Enterprise Guardrails

- **Domain Restriction:** The system uses a global system prompt to politely refuse non-industrial images (e.g., "This appears to be a food item...").
- **Macro-Photography Support:** Explicitly tuned to accept extreme close-ups of broken components (e.g., cracked silicon dies) that generic filters might flag as "abstract" or "unclear."

### 4. Real-Time Telemetry

Every interaction tracks and displays performance metrics to monitor API costs and speed:

- 🪙 **Token Usage:** (Prompt + Completion)
- ⏱️ **Latency:** (Time in seconds)
- ⚡ **Throughput:** (Tokens per second)

### 5. Professional UI/UX

- **Dual Theme Support:** Custom CSS variables for a "Precision Light" mode and a "Cyberpunk Dark" mode optimized for low-light factory floors.
- **PDF Engine:** A custom `fpdf` generator that sanitizes text (removing emojis) to create professional, printable PDF reports.

---

## 🏗️ System Architecture

![System Architecture](docs/screenshots/system_architecture.png)

*Three-layer architecture powering real-time industrial defect detection and analysis*

### Architecture Overview

**Frontend Layer (Streamlit)**
- Sidebar controls for session management and protocol selection
- Image upload widget with drag-and-drop functionality
- Chat-style analysis interface with real-time responses

**Backend Layer (Python)**
- **API Client:** Handles multimodal requests with performance tracking and telemetry
- **Database:** SQLite-based persistent storage for sessions, messages, and image paths
- **Utils:** PDF generation (FPDF) and text sanitization for professional reporting

**AI Layer (Qubrid Vision API)**
- Qwen3-VL-30B multimodal large language model
- Defect detection and severity classification
- Technical analysis and safety audit recommendations

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (Custom CSS, Session State management) |
| **Backend** | Python 3.12 |
| **Database** | SQLite3 (Embedded, zero-config) |
| **AI Provider** | Qubrid AI API (Model: Qwen3-VL-30B) |
| **Reporting** | fpdf2 (PDF generation) |
| **Image Processing** | Pillow, base64 |

---

## 🎨 Features in Action

### 1. Dashboard - Light Mode

![Dashboard Light Mode](docs/screenshots/dashboard_light.png)

*Professional interface optimized for daytime factory operations with component scan and analysis log*

---

### 2. Defect Inspection Mode

![Defect Inspection](docs/screenshots/defect_inspection.png)

*QA failure analysis with structured markdown table showing defect zones, severity levels, and rejection criteria*

---

### 3. Safety Audit - Hazard Detection

![Safety Audit](docs/screenshots/safety_audit_hazard.png)

*Real-time hazard identification with risk matrix categorizing High Risk, Medium Risk, and Compliant elements*

---

### 4. Smart Guardrails - Out of Scope Detection

![Edge Case Handling](docs/screenshots/edge_cases.png)

*Intelligent domain filtering: AI politely refuses non-industrial images (e.g., food items) while maintaining sensitivity for valid technical components. Demonstrates the system's calibration to reject irrelevant inputs without false negatives on legitimate industrial subjects.*

---

### 5. Sidebar Controls - Session Management

![Sidebar Controls](docs/screenshots/1_sidebar_controls.png)

*Clean control panel with session rename/delete functionality and persistent storage*

---

### 6. Protocol Selection

![Protocol Selection](docs/screenshots/2_sidebar_protocols.png)

*Choose between General Analysis, Defect Inspection, or Safety Audit modes with custom focus instructions*

---

### 7. Session Archives

![Session Archives](docs/screenshots/3_sidebar_session_management.png)

*Complete inspection history with timestamp tracking and active session indicator (green dot)*

---

### 8. Dashboard - Dark Mode

![Dashboard Dark Mode](docs/screenshots/dashboard_dark.png)

*Cyberpunk aesthetic for night shift operators with enhanced contrast and reduced eye strain*


---

## 📦 Installation

### Prerequisites

- Python 3.9+
- A Qubrid AI API Key

### 1. Clone the Repository
```bash
git clone https://github.com/aryadoshii-qubrid/diagnostiq.git
cd diagnostiq
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Configuration

Create a `.env` file in the root directory and add your API key:
```ini
QUBRID_API_KEY=your_qubrid_api_key_here
QUBRID_API_URL=https://platform.qubrid.com/api/v1/qubridai/multimodal/chat
QUBRID_MODEL=Qwen/Qwen3-VL-30B-A3B-Instruct
```

### 5. Run the App
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

---

## 📖 Usage Guide

### Quick Start

1. **Select a Mode:** Choose "Defect Inspection" from the sidebar if you are looking for failures.

2. **Upload:** Drag & drop an image of a machine part, PCB, or blueprint.

3. **Analyze:** The AI will automatically scan the image. You can ask follow-up questions like "Is this crack critical?"

4. **Export:** Click "📥 Export PDF" to download a formatted report including the chat history and metrics.

### Analysis Modes

| Mode | Use Case | Output Format |
|------|----------|---------------|
| **General Analysis** | Technical documentation | Structured report with specs |
| **Defect Inspection** | Quality control | Markdown table with severity |
| **Safety Audit** | HSE compliance | Hazard matrix with PPE requirements |

### Example Prompts
```
"Tell me about this component."
"Identify any defects or damage."
"What are the safety risks?"
"Check for cracks in the weld joints."
"What PPE is required to handle this?"
```

---

## 📂 Project Structure
```
diagnostiq/
├── app.py                      # Main entry point & UI layout
├── requirements.txt            # Dependencies
├── .env                        # API Keys (GitIgnored)
├── diagnostiq.db               # Local Database (GitIgnored)
│
├── backend/
│   ├── __init__.py
│   ├── api_client.py          # Handles API requests & Telemetry
│   ├── database.py            # SQLite functions (Init, Add, Delete, Rename)
│   ├── schemas.py             # System Prompts & Guardrails
│   └── utils.py               # PDF Generation & Image Encoding
│
├── frontend/
│   ├── __init__.py
│   ├── components/
│   │   ├── display.py         # Result rendering
│   │   └── uploader.py        # File upload widget
│   ├── sidebar.py             # Sidebar logic & History list
│   ├── styles.py              # CSS for Light/Dark themes
│   └── assets/                # Temporary storage for uploaded images
│
└── config/
    ├── __init__.py
    └── settings.py            # Environment variables
```

---


## 📚 Learn More About Qubrid AI

Explore more applications and tutorials built on the Qubrid AI platform:

### 📖 Resources

- **[Qubrid Cookbook](https://github.com/QubridAI-Inc/qubrid-cookbook)** - Collection of example applications and integration guides
- **[Video Tutorials](https://youtube.com/playlist?list=PLoaE-lmLecgPoYuSa2BsmlJ8isKB5KFtq&si=bbR6pVatRWVtj9e0)** - Step-by-step tutorials and demos
- **[Qubrid Platform](https://platform.qubrid.com)** - Get your API key and explore documentation

---


<p align="center">
  <em>Made with ❤️ by Qubrid AI</em>
</p>
