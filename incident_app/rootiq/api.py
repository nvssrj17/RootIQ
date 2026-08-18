from pathlib import Path

from fastapi import FastAPI, HTTPException

from .investigator import RootIQInvestigator
from .evaluator import RootIQEvaluator


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INCIDENTS_DIR = PROJECT_ROOT / "incidents"

investigator = RootIQInvestigator(PROJECT_ROOT)
evaluator = RootIQEvaluator(INCIDENTS_DIR)

app = FastAPI(
    title="RootIQ AI Incident Investigator",
    description="Evidence-driven AI incident investigation service",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RootIQ"
    }


@app.post("/investigate/{incident_id}")
def investigate_incident(incident_id: str):
    incident_dir = INCIDENTS_DIR / incident_id

    if not incident_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Incident not found: {incident_id}"
        )

    try:
        analysis = investigator.investigate(
            incident_id
        )

        evaluation = evaluator.evaluate(
            incident_id,
            analysis
        )

        return {
            "incident_id": incident_id,
            "investigation": analysis,
            "evaluation": evaluation
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {str(exc)}"
        )