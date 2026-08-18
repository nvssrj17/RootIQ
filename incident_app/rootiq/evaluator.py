import json
from pathlib import Path


class RootIQEvaluator:
    """Evaluates RootIQ investigations against incident ground truth."""

    def __init__(self, incidents_dir: Path):
        self.incidents_dir = incidents_dir

    def load_ground_truth(self, incident_id: str) -> dict:
        """Load the ground-truth definition for an incident."""

        ground_truth_path = (
            self.incidents_dir
            / incident_id
            / "ground_truth.json"
        )

        if not ground_truth_path.exists():
            raise FileNotFoundError(
                f"Ground truth not found: {incident_id}"
            )

        with ground_truth_path.open() as file:
            return json.load(file)

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text for comparison."""

        return (
            text.lower()
            .replace("_", " ")
            .replace("-", " ")
            .strip()
        )

    def evaluate_root_cause(
        self,
        investigation: dict,
        ground_truth: dict
    ) -> bool:
        """Evaluate whether the investigation identified the root cause."""

        predicted = self.normalize(
            investigation.get("root_cause", "")
        )

        expected = self.normalize(
            ground_truth.get("root_cause", "")
        )

        if not predicted or not expected:
            return False

        # Important concepts that should appear in the prediction.
        expected_terms = [
            term
            for term in expected.split()
            if len(term) > 3
        ]

        matches = sum(
            1
            for term in expected_terms
            if term in predicted
        )

        # Require a meaningful portion of the expected
        # root-cause concepts to be present.
        return matches >= max(2, len(expected_terms) * 0.4)

    def evaluate_fix(
        self,
        investigation: dict,
        ground_truth: dict
    ) -> bool:
        """Evaluate whether the recommended fix is aligned."""

        predicted = self.normalize(
            investigation.get("recommended_fix", "")
        )

        expected = self.normalize(
            ground_truth.get(
                "expected_fix",
                ground_truth.get(
                    "recommended_fix",
                    ""
                )
            )
        )

        if not predicted or not expected:
            return False

        expected_terms = [
            term
            for term in expected.split()
            if len(term) > 3
        ]

        matches = sum(
            1
            for term in expected_terms
            if term in predicted
        )

        return matches >= max(2, len(expected_terms) * 0.3)

    def evaluate_files(
        self,
        investigation: dict,
        ground_truth: dict
    ) -> bool | None:
        """Evaluate files when expected files are available."""

        expected_files = ground_truth.get(
            "expected_files"
        )

        if not expected_files:
            return None

        predicted_files = {
            Path(filename).name
            for filename in investigation.get(
                "files_involved",
                []
            )
        }

        expected_files = {
            Path(filename).name
            for filename in expected_files
        }

        if not predicted_files:
            return False

        overlap = expected_files.intersection(
            predicted_files
        )

        return len(overlap) >= 1

    def evaluate(
        self,
        incident_id: str,
        investigation: dict
    ) -> dict:
        """Evaluate a RootIQ investigation."""

        ground_truth = self.load_ground_truth(
            incident_id
        )

        root_cause_correct = self.evaluate_root_cause(
            investigation,
            ground_truth
        )

        fix_correct = self.evaluate_fix(
            investigation,
            ground_truth
        )

        files_correct = self.evaluate_files(
            investigation,
            ground_truth
        )

        checks = [
            root_cause_correct,
            fix_correct
        ]

        if files_correct is not None:
            checks.append(files_correct)

        score = sum(checks) / len(checks)

        return {
            "incident_id": incident_id,
            "root_cause_correct": root_cause_correct,
            "fix_correct": fix_correct,
            "files_correct": files_correct,
            "score": round(score, 2)
        }