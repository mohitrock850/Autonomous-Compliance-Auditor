import asyncio
import json
from google.adk.sessions import InMemorySessionService

from agents.analysis_agent import AnalysisAgent

APP_NAME = "ComplianceAgent"
USER_ID = "test-user"

async def run_test():
    print("--- 🚀 Starting Agent 3 Test (Compliance Analysis) ---")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    
    # --- MOCK DATA (Simulating output from Agent 2) ---
    # We provide a sample "Contract" text that purposefully violates a "Work from Home" policy
    # (assuming your knowledge base has the policy we uploaded earlier)
    mock_jobs = [
        {
            "file_name": "bad_contract.txt",
            "doc_type": "Contract / Agreement",
            "source_id": "mock_id_1",
            "full_content": """
            AGREEMENT SECTION 4: DATA HANDLING
            The contractor is allowed to store company data on their personal unencrypted laptop
            while working from public coffee shops. No VPN is required.
            """
        }
    ]
    session.state["classified_jobs"] = mock_jobs
    
    # Run Agent
    agent = AnalysisAgent()
    session = agent.run(session)
    
    # Check Results
    risks = session.state.get("compliance_risks")
    if risks:
        print(f"\n✅ Success! Found {len(risks)} risks.")
        print(json.dumps(risks, indent=2))
    else:
        print("No risks found (or error occurred).")
        print(session.state.get("error"))

    await session_service.delete_session(session_id=session.id, app_name=APP_NAME, user_id=USER_ID)

if __name__ == "__main__":
    asyncio.run(run_test())