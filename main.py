import asyncio
import os
from google.adk.sessions import InMemorySessionService

# Import all our agents
from agents.ingestion_agent import IngestionAgent
from agents.classification_agent import ClassificationAgent
from agents.analysis_agent import AnalysisAgent
from agents.evidence_agent import EvidenceAgent
from agents.reporting_agent import ReportingAgent

# --- CONFIGURATION ---
# Replace this with your actual Google Drive Folder ID
DRIVE_FOLDER_ID = "1Wq2PM78Tw-wuPGQMRp2hDQzyNxrLor9d" 

# Or use a URL (Comment out DRIVE_FOLDER_ID to use this)
# TARGET_URL = "https://policies.google.com/privacy?hl=en-US"

APP_NAME = "ComplianceAgent"
USER_ID = "demo-user"
YOUR_EMAIL = "mohittherockers@gmail.com"

async def main():
    print("\n" + "="*60)
    print("🚀 STARTING AUTONOMOUS COMPLIANCE SYSTEM")
    print("   (Hybrid RAG + HITL + Self-Reflection)")
    print("="*60 + "\n")

    # 1. Initialize Session
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    session_id_str = session.id
    print(f"✅ Session initialized: {session_id_str}\n")

    try:
        # --- AGENT 1: INGESTION ---
        print("▶️  STEP 1: INGESTION AGENT")
        agent1 = IngestionAgent()
        
        # Prepare input
        if 'DRIVE_FOLDER_ID' in globals() and DRIVE_FOLDER_ID:
            input_data = {"drive_folder_id": DRIVE_FOLDER_ID}
        else:
            input_data = {"url": TARGET_URL}
            
        session = agent1.run(session, input_data)
        if session.state.get("error"): raise Exception(session.state.get("error"))
        print("✅ Ingestion Complete.\n")


        # --- AGENT 2: CLASSIFICATION ---
        print("▶️  STEP 2: CLASSIFICATION AGENT")
        agent2 = ClassificationAgent()
        session = agent2.run(session)
        if session.state.get("error"): raise Exception(session.state.get("error"))
        print("✅ Classification Complete.\n")


        # --- AGENT 3 & 4: ANALYSIS & VERIFICATION LOOP ---
        print("▶️  STEP 3 & 4: ANALYSIS <-> VERIFICATION (SELF-REFLECTION LOOP)")
        
        agent3 = AnalysisAgent()
        agent4 = EvidenceAgent()
        
        MAX_RETRIES = 2
        
        for attempt in range(MAX_RETRIES):
            print(f"\n--- 🔄 Analysis Cycle {attempt + 1}/{MAX_RETRIES} ---")
            
            # Run Analysis (Agent 3)
            session = agent3.run(session)
            if session.state.get("error"): raise Exception(session.state.get("error"))
            
            # Run Verification (Agent 4)
            session = agent4.run(session)
            if session.state.get("error"): raise Exception(session.state.get("error"))
            
            # LOGIC: Check if we need to loop
            verified = session.state.get("verified_risks", [])
            raw_risks = session.state.get("compliance_risks", [])
            
            if verified:
                print("✅ Risks confirmed by Evidence Agent. Proceeding.")
                break
            elif not raw_risks:
                print("✅ No risks found. Analysis is clean. Proceeding.")
                break
            else:
                # Risks were found but rejected (False Positives)
                if attempt < MAX_RETRIES - 1:
                    print("⚠️ Agent 4 rejected all risks. Triggering self-reflection and re-analysis...")
                else:
                    print("⚠️ Max retries reached. Proceeding with zero verified risks.")
        
        print("✅ Analysis & Verification Complete.\n")


        # --- AGENT 5: REPORTING ---
        print("▶️  STEP 5: REPORTING AGENT")
        agent5 = ReportingAgent()
        report_input = {"email_to": YOUR_EMAIL}
        session = agent5.run(session, report_input)
        
        if session.state.get("error"): raise Exception(session.state.get("error"))
        print("✅ Reporting Complete.\n")
        
        print("="*60)
        print("🎉 PIPELINE FINISHED SUCCESSFULLY")
        print(f"📂 Report saved to: {session.state.get('final_report_path')}")
        print(f"📧 Email sent to: {YOUR_EMAIL}")
        print("="*60)

    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        await session_service.delete_session(session_id=session_id_str, app_name=APP_NAME, user_id=USER_ID)
        print("\n(Session closed)")

if __name__ == "__main__":
    asyncio.run(main())