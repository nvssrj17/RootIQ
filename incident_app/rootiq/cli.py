import sys
from pathlib import Path

from .investigator import RootIQInvestigator
from .evaluator import RootIQEvaluator

def main():

    if len(sys.argv) != 2:
        print(
            "Usage: python -m rootiq.cli <incident_id>"
        )
        sys.exit(1)

    incident_id = sys.argv[1]

    project_root = Path(__file__).resolve().parent.parent

    investigator = RootIQInvestigator(project_root)
    evaluator = RootIQEvaluator(
        project_root / "incidents"
    )
    print("=" * 60)
    print("RootIQ - AI Incident Investigation")
    print("=" * 60)

    print(f"\nIncident: {incident_id}")

    print("\nCollecting evidence...")
    analysis = investigator.investigate(incident_id)
    evaluation = evaluator.evaluate(
        incident_id,
        analysis
    )
    print("\n" + "=" * 60)
    print("INVESTIGATION RESULT")
    print("=" * 60)

    print("\nSummary:")
    print(analysis.get("summary", "N/A"))

    print("\nRoot Cause:")
    print(analysis.get("root_cause", "N/A"))

    print("\nEvidence:")

    for item in analysis.get("evidence", []):
        print(f"  • {item}")

    print("\nFiles Involved:")

    for filename in analysis.get("files_involved", []):
        print(f"  • {filename}")

    print("\nRecommended Fix:")
    print(analysis.get("recommended_fix", "N/A"))

    print("\nConfidence:")
    print(analysis.get("confidence", "N/A"))

    print("\n" + "=" * 60)

    print("\n" + "=" * 60)
    print("EVALUATION")
    print("=" * 60)

    print("\nRoot Cause:")
    print(
        "PASS"
        if evaluation["root_cause_correct"]
        else "FAIL"
    )

    print("\nRecommended Fix:")
    print(
        "PASS"
        if evaluation["fix_correct"]
        else "FAIL"
    )

    if evaluation["files_correct"] is not None:
        print("\nFiles Involved:")
        print(
            "PASS"
            if evaluation["files_correct"]
            else "FAIL"
        )

    print("\nOverall Score:")
    print(f"{evaluation['score']:.2f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()