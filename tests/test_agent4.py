import asyncio
import json
from google.adk.sessions import InMemorySessionService
from agents.evidence_agent import EvidenceAgent

APP_NAME = "ComplianceAgent"
USER_ID = "test-user"

async def run_test():
    print("--- 🚀 Starting Agent 4 Test (Verification) ---")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    
    # --- MOCK DATA (Simulating output from Agent 3) ---
    # We pass the risk Agent 3 just found
    mock_risks = [
        {
            "file_name": "bad_contract.txt",
            "chunk_index": 0,
            "severity": "High",
            "description": "Storing company data on unencrypted laptop is bad.",
            "recommendation": "Use VPN.",
            "evidence_excerpt": "\n   The contractor is allowed to store company data on their personal unencrypted laptop\n"
        }
    ]
    session.state["compliance_risks"] = mock_risks
    
    # Run Agent
    agent = EvidenceAgent()
    session = agent.run(session)
    
    # Check Results
    verified = session.state.get("verified_risks")
    
    if verified:
        print(f"\n✅ Success! Verified {len(verified)} risks.")
        print("--- Cleaned Output ---")
        print(json.dumps(verified, indent=2))
    else:
        print("Test failed.")

    await session_service.delete_session(session_id=session.id, app_name=APP_NAME, user_id=USER_ID)

if __name__ == "__main__":
    asyncio.run(run_test())