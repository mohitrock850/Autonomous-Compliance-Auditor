import json
from google.adk.sessions import Session
from models import generate_text

class EvidenceAgent:
    """
    Agent 4: Quality Assurance & Verification (With Human-in-the-Loop).
    """
    
    def __init__(self):
        self.prompt_template = """
        You are a QA Auditor verifying compliance findings.
        
        Review this specific Risk Finding:
        Severity: {severity}
        Description: {description}
        Evidence Excerpt: "{evidence}"

        Task:
        1. Confirm if the Evidence text actually supports the Risk Description.
        2. Polish the Risk Description to be more professional.
        3. Format the Evidence text.

        Return a JSON object:
        {{
            "is_valid": true/false,
            "polished_description": "...",
            "clean_evidence": "..."
        }}
        Return ONLY the JSON.
        """

    def _extract_json(self, text: str) -> dict | None:
        try:
            json_start = text.find('{')
            json_end = text.rfind('}')
            if json_start == -1 or json_end == -1: return None
            return json.loads(text[json_start:json_end+1])
        except: return None

    def _request_human_approval(self, risk):
        """
        Simulates a Human-in-the-Loop approval process.
        """
        print("\n" + "!"*60)
        print(f"🛑 HUMAN INTERVENTION REQUIRED: HIGH SEVERITY RISK DETECTED")
        print(f"File: {risk['file_name']}")
        print(f"Issue: {risk['description']}")
        print("-" * 20)
        print("The system has paused execution to request your approval.")
        # --- THIS IS THE CHANGE: ACTUAL INPUT ---
        print("!"*60 + "\n")
        
        while True:
            user_input = input(">> TYPE 'APPROVE' TO PROCEED OR 'REJECT' TO DROP: ").strip().upper()
            
            if user_input == 'APPROVE':
                print(">> Human Admin: APPROVED.")
                return True
            elif user_input == 'REJECT':
                print(">> Human Admin: REJECTED.")
                return False
            else:
                print("Invalid input. Please type 'APPROVE' or 'REJECT'.")

                
    def run(self, session: Session) -> Session:
        print("--- 🕵️‍♂️ Agent 4: Evidence Verification Agent Running ---")
        
        try:
            raw_risks = session.state.get("compliance_risks")
            if not raw_risks:
                print("No risks to verify. Skipping.")
                return session

            verified_risks = []
            print(f"Verifying {len(raw_risks)} risks...")

            for risk in raw_risks:
                try:
                    prompt = self.prompt_template.format(
                        severity=risk['severity'],
                        description=risk['description'],
                        evidence=risk['evidence_excerpt']
                    )
                    
                    raw_response = generate_text(prompt)
                    result = self._extract_json(raw_response)
                    
                    if result and result.get("is_valid"):
                        risk['description'] = result['polished_description']
                        risk['evidence_excerpt'] = result['clean_evidence']
                        
                        # --- HUMAN IN THE LOOP CHECK ---
                        if risk['severity'] == "High":
                            approved = self._request_human_approval(risk)
                            if not approved:
                                print(f"  🚫 Risk rejected by Human Admin: {risk['file_name']}")
                                continue 
                        # -------------------------------

                        verified_risks.append(risk)
                        print(f"  ✅ Risk verified: {risk['file_name']} ({risk['severity']})")
                    else:
                        print(f"  ❌ Risk rejected (False Positive): {risk['file_name']}")

                except Exception as e:
                    print(f"Error verifying risk: {e}")
                    verified_risks.append(risk)

            session.state["verified_risks"] = verified_risks
            print(f"Verification Complete. {len(verified_risks)} risks confirmed.")

        except Exception as e:
            print(f"Evidence Agent Error: {e}")
            session.state["error"] = str(e)
            
        return session