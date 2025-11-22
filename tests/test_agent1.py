import asyncio
from google.adk.sessions import InMemorySessionService

# Import our new agent
from agents.ingestion_agent import IngestionAgent

# --- Test Configuration ---
DRIVE_FOLDER_ID = "1Wq2PM78Tw-wuPGQMRp2hDQzyNxrLor9d" # Use your folder ID

# We'll define these once
APP_NAME = "ComplianceAgent"
USER_ID = "test-user"


async def run_test():
    print("--- 🚀 Starting Agent 1 Test (Batch Mode) ---")
    
    # 1. Create a new session service
    session_service = InMemorySessionService()
    
    print("Creating a new session...")
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    
    session_id_str = session.id 
    print(f"Session created with ID: {session_id_str}")
    
    # 2. Prepare the input for the agent
    if 'DRIVE_FOLDER_ID' in globals():
        test_input = {"drive_folder_id": DRIVE_FOLDER_ID}
    else:
        test_input = {"url": TEST_URL}
    
    # 3. Create an instance of our agent
    agent = IngestionAgent()
    
    # 4. Run the agent
    print("Calling agent.run()...")
    try:
        session = agent.run(session, test_input)
        
        # 5. Check the session for the agent's output
        print("\n--- ✅ Agent Run Complete. Checking Session Data ---")
        
        # --- THIS IS THE UPDATED CHECK ---
        # We are now looking for 'processing_queue'
        queue = session.state.get("processing_queue")
        error = session.state.get("error")
        
        if error:
            print(f"Agent reported an error: {error}")
        elif queue:
            print(f"Success! Agent created a processing queue with {len(queue)} jobs:")
            import json
            print(json.dumps(queue, indent=2))
        else:
            print("Test failed: Agent ran but did not save 'processing_queue' to session.")
            
    except Exception as e:
        print(f"\n--- ❌ TEST FAILED ---")
        print(f"An error occurred outside the agent: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Clean up the session using the STRING ID
    await session_service.delete_session(
        session_id=session_id_str, app_name=APP_NAME, user_id=USER_ID
    ) 
    print("\n--- 🗑️ Test Complete. Session deleted. ---")


if __name__ == "__main__":
    asyncio.run(run_test())