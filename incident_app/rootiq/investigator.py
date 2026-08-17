from pathlib import Path
import json

from .evidence import EvidenceCollector
from .selector import EvidenceSelector
from .groq_client import GroqClient


class RootIQInvestigator:

    def __init__(self, project_root: Path):
        self.collector = EvidenceCollector(project_root)
        self.selector = EvidenceSelector()
        self.ai = GroqClient()

    def investigate(self, incident_id: str) -> dict:
        """Investigate an incident using collected evidence and AI."""

        # 1. Collect raw evidence
        evidence = self.collector.collect(incident_id)

        # 2. Select relevant evidence
        selected_evidence = self.selector.select(evidence)

        # 3. Prepare evidence for the AI
        evidence_text = json.dumps(
            selected_evidence,
            indent=2
        )

        prompt = f"""
You are RootIQ, an AI incident investigation system.

Your job is to identify the most likely root cause of a
software incident using ONLY the evidence provided below.

Do not invent facts.
Do not assume information that is not present in the evidence.

Analyze:

1. What failed?
2. What is the most likely root cause?
3. What evidence supports the root cause?
4. Which files are involved?
5. What should be fixed?
6. How confident are you?

Return your answer as valid JSON using exactly this structure:

{{
    "summary": "Short description of the incident",
    "root_cause": "Most likely root cause",
    "evidence": [
        "Evidence item 1",
        "Evidence item 2"
    ],
    "files_involved": [
        "file1.py",
        "file2.py"
    ],
    "recommended_fix": "Recommended remediation",
    "confidence": 0.0
}}

INCIDENT EVIDENCE:

{evidence_text}
"""

        # 4. Ask the AI
        response = self.ai.ask(prompt)

        # 5. Parse AI response
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            analysis = {
                "raw_response": response
            }

        # 6. Save investigation result
        incident_dir = (
            self.collector.project_root
            / "incidents"
            / incident_id
            / "evidence"
        )

        incident_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        result_path = (
            incident_dir
            / "investigation_result.json"
        )

        with open(result_path, "w") as f:
            json.dump(
                analysis,
                f,
                indent=2
            )

        return analysis