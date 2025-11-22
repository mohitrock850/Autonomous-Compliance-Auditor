import asyncio
import json
from google.adk.sessions import InMemorySessionService

# Import our new agent
from agents.classification_agent import ClassificationAgent

# We'll define these once
APP_NAME = "ComplianceAgent"
USER_ID = "test-user"


async def run_test():
    print("--- 🚀 Starting Agent 2 Test (Batch Classification) ---")

    # 1. Create a new session service and session
    session_service = InMemorySessionService()
    print("Creating a new session...")
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    session_id_str = session.id 
    print(f"Session created with ID: {session_id_str}")

    # 2. MANUALLY create the 'processing_queue' (Mocking Agent 1's output)
    # We use the exact output from your last successful test
    mock_queue = [
        {
            "source_type": "drive",
            "file_id": "1KqzhESVoe36NVFCqTlDQXtUJ-BpNt4jx",
            "file_name": "internal_policy.docx"
        },
        {
            "source_type": "drive",
            "file_id": "1GyMMZN7Nknw2RVgAr57cwu9VUEBXkmUS",
            "file_name": "test_contract.txt"
        }
    ]

    # Put the "to-do list" into the session
    session.state["processing_queue"] = mock_queue
    print(f"Manually created 'processing_queue' with {len(mock_queue)} jobs.")

    # 3. Create an instance of our agent
    agent = ClassificationAgent()

    # 4. Run the agent
    print("\nCalling agent.run()... This will take a moment (downloading & calling Gemini)...")
    try:
        session = agent.run(session)

        # 5. Check the session for the agent's output
        print("\n--- ✅ Agent Run Complete. Checking Session Data ---")

        # We are now looking for 'classified_jobs'
        classified_jobs = session.state.get("classified_jobs")
        error = session.state.get("error")

        if error:
            print(f"Agent reported an error: {error}")
        elif classified_jobs:
            print(f"Success! Agent created a 'classified_jobs' list with {len(classified_jobs)} results:")
            # Pretty-print the results (but not the full content)
            results_summary = [
                {k: v for k, v in job.items() if k != 'full_content'} 
                for job in classified_jobs
            ]
            print(json.dumps(results_summary, indent=2))
        else:
            print("Test failed: Agent ran but did not save 'classified_jobs' to session.")

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