# 🛡️ Autonomous Compliance Auditor

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white">
  <img alt="Google ADK" src="https://img.shields.io/badge/Google%20ADK-Agent%20Orchestration-orange?logo=google">
  <img alt="Gemini" src="https://img.shields.io/badge/AI-Gemini%202.5%20Flash-8E75B2?logo=google-gemini&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Deployment-Docker-2496ED?logo=docker&logoColor=white">
</p>

---

<p align="center">
  <b>An enterprise-grade multi-agent system that autonomously audits documents, detects risks, and generates compliance reports using Hybrid RAG and Computer Vision.</b>
</p>

---

## 📖 Overview

The **Autonomous Compliance Auditor** transforms the slow, manual, and error-prone process of legal document review into a high-speed, AI-driven pipeline.

Designed for the **Enterprise Agents** track, this system uses a team of **5 specialized AI Agents** to autonomously monitor cloud storage, read complex documents (including scanned images via OCR), identify non-compliance risks using **Hybrid RAG**, and generate audit-ready reports.

Critically, it features a **Human-in-the-Loop (HITL)** guardrail for high-severity risks, ensuring enterprise safety and accountability.

### 🖥️ The Dashboard
The system provides a real-time **Compliance Dashboard** to visualize the audit process and handle approvals.

![Full Dashboard](./screenshots/dashboard-full.png)

---

## 🚀 Key Features & Innovation

| Feature | Description |
|----------|--------------|
| 🧠 **Hybrid RAG Brain** | Combines **Vector Search** (FAISS) for concepts, **Keyword Search** (BM25) for exact terms, and **Cross-Encoder Re-Ranking** to find precise policy clauses with extreme accuracy. |
| 🔄 **Self-Reflection Loop** | If the QA Agent rejects a finding (false positive), the system triggers a **self-correction cycle**, asking the Analyst Agent to re-evaluate the document automatically. |
| 👁️ **Agentic Vision (OCR)** | Uses **Gemini 2.5 Flash Vision** to "see" and transcribe scanned contracts, charts, and screenshots that traditional text parsers miss. |
| 🛑 **Human-in-the-Loop** | **Enterprise Safety:** High-severity risks trigger a blocking state, pausing the pipeline and requiring human approval via the UI before the report is finalized. |
| 🕵️ **Multi-Agent Pipeline** | A choreographed workflow of 5 agents: *Ingestion, Classification, Analysis, Evidence, Reporting*. |

---

## 🧠 System Architecture

The system is built on the **Google Agent Development Kit (ADK)** using a "Loop-and-Gate" pattern.



1.  **User** starts Audit via Streamlit UI.
2.  **Ingestion Agent** scans Google Drive/URLs and queues files.
3.  **Classification Agent** identifies document type.
    * If Image/Scanned PDF -> Uses **Vision Tool**.
    * If Text Doc -> Uses **File Reader**.
4.  **Analysis Agent** chunks text and queries **Hybrid RAG DB** for policies.
5.  **Evidence Agent** verifies risks.
    * If Invalid -> Triggers **Self-Reflection Loop** back to Analysis.
    * If Valid & High Severity -> Triggers **HITL Pause**.
6.  **Human Admin** approves or rejects via Dashboard.
7.  **Reporting Agent** emails final report to user.

---

## 📸 Application Walkthrough

### 1. Risk Detection & HITL Guardrail
When a "High Severity" risk is detected (e.g., insecure data handling), the system automatically **pauses** and demands human review.

![HITL Warning](./screenshots/hitl-warning.png)

### 2. Comprehensive Reporting
The system generates a detailed Markdown report, categorizing risks by severity (High/Medium/Low) with clear evidence and recommendations.

![Report Summary](./screenshots/report-summary.png)
![Report Findings](./screenshots/report-findings.png)
![Report Details](./screenshots/report-details.png)

### 3. Automated Delivery
Once approved, the final report is automatically emailed to the stakeholders.

![Email Proof](./screenshots/email-proof.png)

---

## 🛠️ Tech Stack

* **Orchestration:** Google ADK (Agent Development Kit)
* **LLM:** Gemini 2.5 Flash (Reasoning, Vision, Classification)
* **Frontend:** Streamlit (Interactive Dashboard)
* **Vector DB:** FAISS (Semantic Search)
* **Re-Ranking:** Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
* **Tools:** Google Drive API, Gmail API
* **OCR:** Pillow & Gemini Vision

---

## 🏃‍♂️ Getting Started

### 1️⃣ Prerequisites
* Python 3.10+
* A Google Cloud Project with **Drive API** and **Gmail API** enabled.
* A Google AI Studio API Key.

### 2️⃣ Installation

Clone the repository and install dependencies:

```bash
git clone [https://github.com/yourusername/autonomous-compliance-auditor.git](https://github.com/yourusername/autonomous-compliance-auditor.git)
cd autonomous-compliance-auditor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install libraries
pip install -r requirements.txt
3️⃣ Configuration
Environment Variables: Create a .env file in the root directory:

Ini, TOML

GEMINI_API_KEY="your_google_ai_studio_key"
Google Credentials: Place your credentials.json (OAuth 2.0 Client ID) in the root folder.

Build Knowledge Base:

Put your PDF/TXT policy documents in the knowledge_base/ folder.

Run the indexer to build the RAG brain:

Bash

python run_indexing.py
🖥️ Usage
Option A: Run with Docker (Recommended)
We have containerized the application for easy deployment.

Bash

# Build the image
docker build -t compliance-ai .

# Run the container (Mounting secrets)
docker run -p 8501:8501 \
  --env-file .env \
  -v ${PWD}/credentials.json:/app/credentials.json \
  -v ${PWD}/token.json:/app/token.json \
  compliance-ai
Access the dashboard at http://localhost:8501.

Option B: Run Locally
Bash

streamlit run app.py
🏆 Competition Track: Enterprise Agents
This project addresses a critical enterprise need—Compliance Automation. It moves beyond simple chat interactions to perform complex, long-running background work that integrates with existing business tools (Drive/Email) while maintaining strict human oversight for high-risk decisions.