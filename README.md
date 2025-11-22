# 🛡️ Autonomous Compliance Auditor

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Orchestration-orange?logo=google)](https://github.com/google/adk-python)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-8E75B2?logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**An enterprise-grade multi-agent system that autonomously audits documents, detects risks via Hybrid RAG, and enforces Human-in-the-Loop safety.**

</div>

---

## 📸 Live Dashboard
![Main Dashboard](./screenshots/dashboard.png)

---

## ⚡ Key Features

| Feature | Tech | Description |
| :--- | :--- | :--- |
| 🧠 **Hybrid Brain** | **FAISS + BM25** | Combines vector & keyword search with **Cross-Encoder Re-Ranking** for precise policy retrieval. |
| 👁️ **Agentic Vision** | **Gemini Vision** | Transcribes scanned contracts, charts, and images that standard parsers miss. |
| 🛑 **Safety Guardrail** | **HITL** | **Stops execution** on high-severity risks until a human admin approves via UI. |
| 🔄 **Self-Healing** | **Reflection Loop** | If a finding is rejected, the agent automatically re-analyzes the document. |
| 🕵️ **Orchestration** | **Google ADK** | Coordinates 5 agents: *Ingestion, Classification, Analysis, Evidence, Reporting*. |

---

## 🔄 Architecture Flow

The system uses a **Loop-and-Gate** pattern to ensure accuracy and safety.

```mermaid
graph TD
    Start[🚀 Start Audit] --> Ingest[🕵️ Ingestion Agent]
    Ingest --> Classify[🧐 Classification Agent]
    
    subgraph "Perception Layer"
    Classify -- Image --> Vision[👁️ Vision Tool]
    Classify -- Text --> File[📄 File Reader]
    end

    Vision --> Analyze[⚖️ Analysis Agent]
    File --> Analyze
    
    subgraph "Cognitive Loop"
    Analyze <-->|Hybrid RAG Query| DB[(Policy DB)]
    Analyze --> Evidence[🕵️‍♂️ Evidence Agent]
    Evidence -- Reject --> Analyze
    end
    
    Evidence -- Verify --> Gate{Severity?}
    Gate -- High --> HITL[🛑 Human Approval]
    Gate -- Low --> Report[📝 Reporting Agent]
    HITL --> Report
    
    Report --> Email[📧 Email User]
    Report --> UI[🖥️ Update Dashboard]

    style HITL fill:#b71c1c,stroke:#fff,color:#fff
    style Analyze fill:#0d47a1,stroke:#fff,color:#fff
```
## Workflow Gallery 

<div align="center">
  <h3>Screenshots</h3>
  <table border="0" cellspacing="10" cellpadding="10">
    <tr>
      <td align="center">
        <strong>Risk Detected</strong><br><br>
        <img src="./screenshots/report-findings.png" alt="Full Q&A conversation" width="400">
      </td>
      <td align="center">
        <strong>HITL Guardrail</strong><br><br>
        <img src="./screenshots/hitl-warning.png" alt="Initial application screen with configuration sidebar" width="400">
      </td>
    </tr>
    <tr>
      <td align="center">
        <strong>Final Report</strong><br><br>
        <img src="./screenshots/report-summary.png" alt="Showing retrieved evidence from the vector search" width="400">
      </td>
      <td align="center">
        <strong>Delivery</strong><br><br>
        <img src="./screenshots/email-proof.png" alt="Showing retrieved evidence from the knowledge graph" width="400">
      </td>
    </tr>
  </table>
</div>

## 🛠️ Tech Stack

This project is built with a robust, enterprise-grade stack of tools and libraries:

<p align="center">
  <a href="https://www.python.org" target="_blank">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://github.com/google/adk-python" target="_blank">
    <img src="https://img.shields.io/badge/Google%20ADK-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google ADK">
  </a>
  <a href="https://streamlit.io" target="_blank">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  </a>
  <a href="https://ai.google.dev/" target="_blank">
    <img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=google-gemini&logoColor=white" alt="Gemini">
  </a>
  <a href="https://www.docker.com/" target="_blank">
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  </a>
  <a href="https://github.com/facebookresearch/faiss" target="_blank">
    <img src="https://img.shields.io/badge/FAISS-0081CB?style=for-the-badge&logo=meta&logoColor=white" alt="FAISS">
  </a>
  <a href="https://huggingface.co/" target="_blank">
    <img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace">
  </a>
</p>

## Getting Started

Follow these steps to set up and run the Autonomous Compliance Auditor locally.

### Prerequisites

-   Python 3.10+
-   Git
-   Google Cloud Project (with Drive & Gmail APIs enabled)
-   Google AI Studio API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/autonomous-compliance-auditor.git](https://github.com/yourusername/autonomous-compliance-auditor.git)
    cd autonomous-compliance-auditor
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate
    
    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Configuration:**
    * Create a `.env` file in the root directory:
        ```ini
        GEMINI_API_KEY="your_google_ai_studio_key"
        ```
    * Place your `credentials.json` (Google OAuth Client ID) in the root folder.

## Usage

1.  **Build the Knowledge Base:**
    Run the indexer to vectorize your policy documents (PDF/TXT in `knowledge_base/`):
    ```bash
    python run_indexing.py
    ```

2.  **Launch the Dashboard:**
    Start the Streamlit application:
    ```bash
    streamlit run app.py
    ```

3.  **Access the App:**
    Open your web browser to the local URL provided (usually `http://localhost:8501`).

4.  **Run an Audit:**
    * Enter a **Google Drive Folder ID** or **Web URL** in the sidebar.
    * Click **"🚀 Start Audit Pipeline"**.
    * Watch the agents ingest, classify, and analyze files in real-time.
    * **Approve/Reject** high-severity risks when the Human-in-the-Loop guardrail activates.

## Documents Tested

This system has been successfully tested on complex enterprise documents, including:
-   `Internal_Data_Policy.docx` (Text-based policies)
-   `Scanned_Vendor_Contract.png` (Image-based contracts requiring OCR)
-   `Google_Privacy_Policy.html` (Live web URLs)
