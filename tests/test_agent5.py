import asyncio
from google.adk.sessions import InMemorySessionService
from agents.reporting_agent import ReportingAgent

APP_NAME = "ComplianceAgent"
USER_ID = "test-user"

async def run_test():
    print("--- 🚀 Starting Agent 5 Test (Reporting) ---")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    
    # --- MOCK DATA (Output from Agent 4) ---
    mock_verified_risks = [
        {
            "file_name": "bad_contract.txt",
            "chunk_index": 0,
            "severity": "High",
            "description": "Company data is stored on unencrypted personal laptops, violating data security policies.",
            "recommendation": "Enforce VPN usage and ban unencrypted devices.",
            "evidence_excerpt": "contractor is allowed to store company data on their personal unencrypted laptop"
        }
    ]
    session.state["verified_risks"] = mock_verified_risks
    
    # Run Agent
    agent = ReportingAgent()
    
    # We can pass the email here if we want to override the default
    input_data = {"email_to": "mohittherockers@gmail.com"}
    
    session = agent.run(session, input_data)
    
    if session.state.get("report_sent"):
        print("\n✅ Success! Report generated and email sent.")
    else:
        print("\n❌ Test Failed.")

    await session_service.delete_session(session_id=session.id, app_name=APP_NAME, user_id=USER_ID)

if __name__ == "__main__":
    asyncio.run(run_test())