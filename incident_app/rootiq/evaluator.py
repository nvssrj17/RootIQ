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

        aliases = {
            "misconfigured": "configuration",
            "incorrectly configured": "configuration",
            "configuration": "configuration",
            "configured": "configuration",
            "connection refused": "connection",
            "unreachable": "connection",
            "connection": "connection",
            "notification service": "notification",
            "notification": "notification",
            "endpoint": "endpoint",
            "url": "endpoint",
            "notification url": "endpoint",
            "localhost:9999": "endpoint",
            "database schema": "schema",
            "schema mismatch": "schema",
            "schema": "schema",
            "database": "database",
            "sqlite": "database",
            "customer email": "customer_email"
        }

        concepts = set()

        for phrase, concept in aliases.items():
            if phrase in expected:
                concepts.add(concept)

        if not concepts:
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

            return matches >= max(
                2,
                len(expected_terms) * 0.4
            )

        matched_concepts = 0

        for concept in concepts:

            if concept == "configuration":
                if any(
                    phrase in predicted
                    for phrase in [
                        "configuration",
                        "configured",
                        "misconfigured"
                    ]
                ):
                    matched_concepts += 1

            elif concept == "connection":
                if any(
                    phrase in predicted
                    for phrase in [
                        "connection",
                        "connection refused",
                        "unreachable",
                        "cannot establish"
                    ]
                ):
                    matched_concepts += 1

            elif concept == "notification":
                if "notification" in predicted:
                    matched_concepts += 1

            elif concept == "endpoint":
                if any(
                    phrase in predicted
                    for phrase in [
                        "endpoint",
                        "url",
                        "localhost:9999",
                        "notification url"
                    ]
                ):
                    matched_concepts += 1

            elif concept == "schema":
                if any(
                    phrase in predicted
                    for phrase in [
                        "schema",
                        "schema mismatch",
                        "table"
                    ]
                ):
                    matched_concepts += 1

            elif concept == "database":
                if any(
                    phrase in predicted
                    for phrase in [
                        "database",
                        "sqlite",
                        "sqlite3"
                    ]
                ):
                    matched_concepts += 1

            elif concept == "customer_email":
                if any(
                    phrase in predicted
                    for phrase in [
                        "customer email",
                        "customer_email"
                    ]
                ):
                    matched_concepts += 1

        match_ratio = matched_concepts / len(concepts)

        return match_ratio >= 0.5

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

        return matches >= max(
            2,
            len(expected_terms) * 0.3
        )

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
        """Evaluate and save a RootIQ investigation."""

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

        evaluation_result = {
            "incident_id": incident_id,
            "root_cause_correct": root_cause_correct,
            "fix_correct": fix_correct,
            "files_correct": files_correct,
            "score": round(score, 2)
        }

        output_dir = (
            self.incidents_dir
            / incident_id
            / "evidence"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = (
            output_dir
            / "evaluation_result.json"
        )

        with output_path.open("w") as file:
            json.dump(
                evaluation_result,
                file,
                indent=2
            )

        return evaluation_result