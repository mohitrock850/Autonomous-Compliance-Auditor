import json
import os
from datetime import datetime
from google.adk.sessions import Session
from models import generate_text
from tools.notification_tool import send_email_report

class ReportingAgent:
    """
    Agent 5: Generates the final report and sends notifications.
    """
    
    def __init__(self):
        self.summary_prompt = """
        You are a Chief Compliance Officer writing an executive summary for an audit report.
        
        Review these confirmed risks:
        {risks_json}

        Write a 1-paragraph Executive Summary (approx 200 words).
        - Highlight the total number of risks and the highest severity found.
        - Summarize the main themes (e.g., "Data Security gaps").
        - Keep it professional and urgent if necessary.
        """

    def run(self, session: Session, input_data: dict = None) -> Session:
        print("--- 📝 Agent 5: Reporting Agent Running ---")
        
        try:
            risks = session.state.get("verified_risks", [])
            
            # 1. Generate the Executive Summary
            if not risks:
                summary = "No compliance risks were detected during this scan. All documents appear to meet regulatory standards."
                print("No risks found. Generating clean report.")
            else:
                print("Generating Executive Summary with Gemini...")
                # Convert risks to string for the prompt
                risks_str = json.dumps([{k:v for k,v in r.items() if k != 'full_content'} for r in risks])
                prompt = self.summary_prompt.format(risks_json=risks_str)
                summary = generate_text(prompt)

            # 2. Build the Markdown Report
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_lines = []
            report_lines.append(f"# Compliance Audit Report")
            report_lines.append(f"**Date:** {timestamp}")
            report_lines.append(f"\n## Executive Summary")
            report_lines.append(summary)
            
            if risks:
                report_lines.append(f"\n## Detailed Findings ({len(risks)} Total)")
                for i, risk in enumerate(risks, 1):
                    icon = "🔴" if risk['severity'] == "High" else "Ez" if risk['severity'] == "Medium" else "🔵"
                    report_lines.append(f"\n### {i}. {icon} {risk['severity']} Risk: {risk['file_name']}")
                    report_lines.append(f"**Description:** {risk['description']}")
                    report_lines.append(f"**Evidence:** _{risk['evidence_excerpt']}_")
                    report_lines.append(f"**Recommendation:** {risk['recommendation']}")
                    report_lines.append("---")
            
            report_content = "\n".join(report_lines)
            
            # 3. Save to File
            report_filename = "Final_Compliance_Report.md"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            print(f"Report saved locally to: {report_filename}")
            
            # 4. Email the Report
            # Get email from input, or default to yours
            recipient = input_data.get("email_to") if input_data else "mohittherockers@gmail.com"
            
            print(f"Sending email to {recipient}...")
            subject = f"Compliance Audit Report - {timestamp}"
            body = f"Please find attached the latest compliance audit report.\n\nExecutive Summary:\n{summary}"
            
            # Call our tool
            email_status = send_email_report(recipient, subject, body, report_filename)
            print(email_status)
            
            session.state["report_sent"] = True
            session.state["final_report_path"] = report_filename

        except Exception as e:
            print(f"Reporting Agent Error: {e}")
            session.state["error"] = str(e)
            
        return session