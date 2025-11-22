import streamlit as st
import asyncio
import json
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Import ADK and Agents
from google.adk.sessions import InMemorySessionService
from agents.ingestion_agent import IngestionAgent
from agents.classification_agent import ClassificationAgent
from agents.analysis_agent import AnalysisAgent
from agents.evidence_agent import EvidenceAgent
from agents.reporting_agent import ReportingAgent

# Page Config
st.set_page_config(page_title="ComplianceAI Dashboard", page_icon="🛡️", layout="wide")
load_dotenv()

# --- 1. ENHANCED VISUAL UPGRADES (Custom CSS) ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1a73e8; font-weight: 800; margin-bottom: 0px;}
    .sub-tagline {font-size: 0.9rem; color: #666; margin-bottom: 30px;}
    .card {background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #3b3b42; margin-bottom: 10px;}
    .risk-high {background-color: #d32f2f; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;}
    .risk-med {background-color: #f57f17; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;}
    .risk-low {background-color: #388e3c; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;}
    .metric-box {text-align: center; border: 1px solid #eee; border-radius: 5px; padding: 10px; background: white;}
    
    /* Report Specific Styles */
    .report-title {font-size: 2rem; color: #1a73e8; font-weight: 700; margin-top: 30px;}
    .report-date {font-size: 0.9rem; color: #999; margin-bottom: 20px;}
    .section-header {font-size: 1.5rem; color: #1a73e8; font-weight: 600; margin-top: 25px; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;}
    .summary-text {font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px; color: #e0e0e0;}
    .finding-card {background-color: #31333f; border: 1px solid #4f535d; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
    .finding-title {font-size: 1.2rem; color: #e0e0e0; font-weight: 600; margin-bottom: 10px;}
    .finding-detail {font-size: 0.95rem; margin-bottom: 5px; color: #bdbdbd;}
    .recommendation-header {font-size: 1rem; color: #1a73e8; font-weight: 600; margin-top: 15px; margin-bottom: 5px;}
    .recommendation-text {font-size: 0.95rem; line-height: 1.5; color: #a0a0a0;}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE SETUP ---
if 'adk_service' not in st.session_state:
    st.session_state['adk_service'] = InMemorySessionService()

if 'pipeline_state' not in st.session_state:
    st.session_state['pipeline_state'] = "IDLE" # IDLE, RUNNING, WAITING_APPROVAL, APPROVED, COMPLETED
if 'risks' not in st.session_state:
    st.session_state['risks'] = []
if 'session_obj_id' not in st.session_state:
    st.session_state['session_obj_id'] = None
if 'final_report_content' not in st.session_state: # To store structured report
    st.session_state['final_report_content'] = {}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=50)
    st.header("Configuration")
    app_mode = st.radio("Input Source", ["Google Drive", "Web URL"])
    
    folder_id = ""
    target_url = ""
    if app_mode == "Google Drive":
        folder_id = st.text_input("Drive Folder ID", value="1Wq2PM78Tw-wuPGQMRp2hDQzyNxrLor9d")
    else:
        target_url = st.text_input("Target URL", value="https://policies.google.com/privacy?hl=en-US")
    
    user_email = st.text_input("Report Recipient", value="mohittherockers@gmail.com")
    
    st.divider()
    
    if st.button("🚀 Start Audit Pipeline", type="primary", key="start_audit"):
        st.session_state['pipeline_state'] = "RUNNING"
        st.session_state['risks'] = [] 
        st.session_state['session_obj_id'] = None
        st.session_state['final_report_content'] = {}
        st.session_state['adk_service'] = InMemorySessionService() # Clean slate
        st.rerun()

# --- 4. MAIN LAYOUT ---
st.markdown('<p class="main-header">Autonomous Compliance Auditor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-tagline">Leveraging Gemini for proactive risk detection and automated reporting</p>', unsafe_allow_html=True)


# Status Bar (Top)
status_container = st.container()

# Two Columns for Live Updates
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📁 Ingestion & Classification")
    ingest_container = st.empty()
    classify_container = st.empty()

with col2:
    st.subheader("⚖️ Risk Analysis")
    analysis_container = st.empty()

# Approval & Report Area (Bottom)
action_container = st.container()
report_container = st.container()

# --- PIPELINE FUNCTIONS ---

async def run_phase_1_analysis():
    """Runs Agents 1-4 (Ingestion -> Verification)"""
    session = await st.session_state['adk_service'].create_session(app_name="ComplianceApp", user_id="streamlit-user")
    st.session_state['session_obj_id'] = session.id
    
    try:
        # --- Agent 1: Ingestion ---
        with status_container: st.info("🕵️ Agent 1: Scanning source...", icon="⏳")
        agent1 = IngestionAgent()
        input_data = {"drive_folder_id": folder_id} if app_mode == "Google Drive" else {"url": target_url}
        session = agent1.run(session, input_data)
        
        queue = session.state.get("processing_queue", [])
        with ingest_container:
            st.success(f"**Ingestion:** Found {len(queue)} files.")
            st.dataframe(pd.DataFrame(queue), height=150, use_container_width=True)

        # --- Agent 2: Classification ---
        with status_container: st.info("🧐 Agent 2: Classifying documents...", icon="⏳")
        agent2 = ClassificationAgent()
        session = agent2.run(session)
        
        classified = session.state.get("classified_jobs", [])
        with classify_container:
            st.success(f"**Classification:** Processed {len(classified)} docs.")
            if classified:
                st.table(pd.DataFrame(classified)[['file_name', 'doc_type']].set_index('file_name'))

        # --- Agent 3 & 4: Analysis Loop ---
        with status_container: st.info("⚖️ Agent 3 & 4: Analyzing risks (Hybrid RAG)...", icon="⏳")
        agent3 = AnalysisAgent()
        agent4 = EvidenceAgent()
        
        # Simple loop (1 retry)
        for _ in range(2):
            session = agent3.run(session)
            session = agent4.run(session)
            if session.state.get("verified_risks") or not session.state.get("compliance_risks"):
                break
        
        risks = session.state.get("verified_risks", [])
        st.session_state['risks'] = risks # Store risks for later display/report
        
        high_risks = [r for r in risks if r['severity'] == 'High']
        
        if high_risks:
            st.session_state['pipeline_state'] = "WAITING_APPROVAL"
            with status_container: st.warning("⚠️ High Risks Detected! Waiting for Approval...", icon="🛑")
        else:
            st.session_state['pipeline_state'] = "APPROVED" 
            
        st.rerun() 

    except Exception as e:
        st.error(f"Error in Phase 1: {e}")
        import traceback
        st.code(traceback.format_exc())

async def run_phase_2_reporting():
    """Runs Agent 5 (Reporting) and displays the formatted report"""
    try:
        session_id = st.session_state['session_obj_id']
        if not session_id:
            st.error("Session ID lost. Please restart the audit.")
            return

        session = await st.session_state['adk_service'].get_session(
            session_id=session_id, 
            app_name="ComplianceApp", 
            user_id="streamlit-user"
        )
        
        if not session:
            st.error("Could not retrieve session from memory. Service may have reset.")
            return

        with status_container: st.info("📝 Agent 5: Generating Report...", icon="⏳")
        
        session.state["verified_risks"] = st.session_state['risks'] # Ensure risks are present for reporting
        
        agent5 = ReportingAgent()
        session = agent5.run(session, {"email_to": user_email})
        
        report_path = session.state.get('final_report_path')
        
        # --- ENHANCED REPORT DISPLAY ---
        with report_container:
            st.markdown("---")
            st.balloons()
            st.success(f"✅ Report emailed to {user_email}")
            
            if report_path and os.path.exists(report_path):
                with open(report_path, "r") as f:
                    report_content_md = f.read()

                # Parse the Markdown content to extract structured data
                # This is a simplified parser, for a very complex report, you'd use regex or a markdown parser lib
                report_lines = report_content_md.split('\n')
                
                # Extract Title, Date, Executive Summary
                title = "Compliance Audit Report"
                report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                executive_summary = ""
                findings_start_idx = -1

                for i, line in enumerate(report_lines):
                    if line.startswith('Date:'):
                        report_date = line.replace('Date:', '').strip()
                    elif line.startswith('## Executive Summary'):
                        findings_start_idx = i + 1
                        break
                
                if findings_start_idx != -1:
                    # Find the start of "Detailed Findings"
                    detailed_findings_header_idx = -1
                    for i in range(findings_start_idx, len(report_lines)):
                        if report_lines[i].startswith('## Detailed Findings'):
                            detailed_findings_header_idx = i
                            break
                    
                    if detailed_findings_header_idx != -1:
                        executive_summary = "\n".join(report_lines[findings_start_idx:detailed_findings_header_idx]).strip()
                    else:
                        executive_summary = "\n".join(report_lines[findings_start_idx:]).strip() # No detailed findings section

                
                # Display Report Header
                st.markdown(f'<p class="report-title">{title}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="report-date">Date: {report_date}</p>', unsafe_allow_html=True)

                # Executive Summary
                st.markdown('<p class="section-header">Executive Summary</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="summary-text">{executive_summary}</p>', unsafe_allow_html=True)
                
                # Detailed Findings (if any)
                if st.session_state['risks']:
                    st.markdown('<p class="section-header">Detailed Findings</p>', unsafe_allow_html=True)
                    for i, r in enumerate(st.session_state['risks']):
                        color_class = "risk-high" if r['severity'] == 'High' else "risk-med"
                        st.markdown(f"""
                        <div class="finding-card">
                            <p class="finding-title">
                                <span class="{color_class}">{r['severity']}</span> Finding #{i+1}: {r['file_name']}
                            </p>
                            <p class="finding-detail"><b>Issue:</b> {r['description']}</p>
                            <p class="finding-detail"><b>Evidence Excerpt:</b> <i>"{r['evidence_excerpt']}"</i></p>
                            <p class="recommendation-header">Recommendation:</p>
                            <p class="recommendation-text">{r['recommendation']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No detailed findings for this audit (no risks verified).")
                
                # Download Button
                st.download_button(
                    label="📥 Download Full Report",
                    data=report_content_md,
                    file_name=f"Compliance_Audit_Report_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )

        with status_container: st.success("Pipeline Complete!", icon="✅")
        st.session_state['pipeline_state'] = "COMPLETED"
        
        await st.session_state['adk_service'].delete_session(
            session_id=session.id, 
            app_name="ComplianceApp", 
            user_id="streamlit-user"
        )

    except Exception as e:
        st.error(f"Reporting Error: {e}")
        import traceback
        st.code(traceback.format_exc())

# --- LOGIC CONTROLLER ---

if st.session_state['pipeline_state'] == "RUNNING":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_phase_1_analysis())

# Show Risks (Always show if we have them and pipeline is not yet completed)
if st.session_state['risks'] and st.session_state['pipeline_state'] not in ["IDLE", "RUNNING", "COMPLETED"]:
    with analysis_container:
        risks = st.session_state['risks']
        st.subheader("Detected Risks")
        if risks:
            total_risks = len(risks)
            high_count = sum(1 for r in risks if r['severity'] == 'High')
            st.markdown(f"""
            <div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
                <div class="metric-box"><b>Total</b><br>{total_risks}</div>
                <div class="metric-box" style="color: {'red' if high_count > 0 else 'green'};"><b>High Severity</b><br>{high_count}</div>
            </div>
            """, unsafe_allow_html=True)
            
            for r in risks:
                color_class = "risk-high" if r['severity'] == 'High' else "risk-med" if r['severity'] == 'Medium' else "risk-low"
                st.markdown(f"""
                <div class="card">
                    <span class="{color_class}">{r['severity']}</span> <b>{r['file_name']}</b><br>
                    <small>{r['description']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No risks detected in analysis phase.")


if st.session_state['pipeline_state'] == "WAITING_APPROVAL":
    with action_container:
        st.divider()
        st.error("🛑 **Human Intervention Required:** High Severity risks were detected. Review findings and approve to generate the final report.", icon="🚨")
        c1, c2 = st.columns(2)
        if c1.button("✅ APPROVE & GENERATE REPORT", type="primary", use_container_width=True, key="approve_button"):
            st.session_state['pipeline_state'] = "APPROVED"
            st.rerun()
        if c2.button("❌ REJECT & ABORT", type="secondary", use_container_width=True, key="reject_button"):
            st.error("Audit Rejected. Pipeline terminated.")
            st.session_state['pipeline_state'] = "COMPLETED" # Consider a 'REJECTED' state
            st.stop()


if st.session_state['pipeline_state'] == "APPROVED":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_phase_2_reporting())

if st.session_state['pipeline_state'] == "COMPLETED":
    with action_container: # Or a dedicated end-state container
        if st.button("Start New Audit", key="new_audit_button"):
            st.session_state['pipeline_state'] = "IDLE"
            st.session_state['risks'] = []
            st.session_state['session_obj_id'] = None
            st.session_state['final_report_content'] = {}
            st.session_state['adk_service'] = InMemorySessionService()
            st.rerun()