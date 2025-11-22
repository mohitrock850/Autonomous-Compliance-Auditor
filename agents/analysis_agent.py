import json
from google.adk.sessions import Session
from models import generate_text
from tools.rag_tool import query_knowledge_base

class AnalysisAgent:
    """
    Agent 3: Analyzes documents for compliance risks.
    It uses RAG (Retrieval Augmented Generation) to check documents
    against the internal knowledge base.
    """
    
    def __init__(self):
        # We use double brackets {{ }} for JSON examples in the prompt
        self.prompt_template = """
        You are a senior Compliance Officer. 
        Analyze the following "Target Text" (from a {doc_type}) against the "Relevant Policies" provided.

        Target Text:
        "{chunk_text}"

        Relevant Policies (Context):
        {rag_context}

        Task:
        Identify if there is a compliance risk, conflict, or missing requirement.
        If the text is compliant, return null.
        If there is a risk, describe it.

        Return a JSON object with this format:
        {{
            "has_risk": true/false,
            "risk_severity": "High" | "Medium" | "Low",
            "risk_description": "Short explanation of the conflict",
            "recommendation": "What should be changed"
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

    def _chunk_text(self, text, chunk_size=2000):
        """Simple helper to split long docs into manageable pieces"""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def run(self, session: Session) -> Session:
        print("--- ⚖️ Agent 3: Compliance Analysis Agent Running ---")
        
        try:
            jobs = session.state.get("classified_jobs")
            if not jobs: raise Exception("No classified jobs found.")
            
            all_risks = []

            for job in jobs:
                # Skip files that failed previous steps
                if job.get("doc_type") == "Error" or not job.get("full_content"):
                    continue

                print(f"Analyzing: {job['file_name']} ({job['doc_type']})")
                
                # 1. Split document into chunks
                chunks = self._chunk_text(job['full_content'])
                print(f"-> Split into {len(chunks)} chunks for analysis.")

                for i, chunk in enumerate(chunks):
                    # 2. Use RAG to find relevant policies for this specific chunk
                    # We search the knowledge base using the chunk text itself
                    rag_context = query_knowledge_base(chunk)
                    
                    # 3. Ask Gemini to analyze
                    prompt = self.prompt_template.format(
                        doc_type=job['doc_type'],
                        chunk_text=chunk,
                        rag_context=rag_context
                    )
                    
                    raw_response = generate_text(prompt)
                    result = self._extract_json(raw_response)

                    # 4. If a risk is found, save it
                    if result and result.get("has_risk"):
                        print(f"  ⚠️ Risk Found in Chunk {i+1}: {result['risk_severity']}")
                        all_risks.append({
                            "file_name": job['file_name'],
                            "chunk_index": i,
                            "severity": result['risk_severity'],
                            "description": result['risk_description'],
                            "recommendation": result['recommendation'],
                            "evidence_excerpt": chunk[:200] + "..." # Store snippet for report
                        })
            
            # Save all found risks to session
            session.state["compliance_risks"] = all_risks
            print(f"Analysis Complete. Found {len(all_risks)} total risks.")

        except Exception as e:
            print(f"Analysis Agent Error: {e}")
            session.state["error"] = str(e)
            
        return session