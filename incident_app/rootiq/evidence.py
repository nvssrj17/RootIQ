from pathlib import Path
import json
import subprocess


class EvidenceCollector:
    """Collects investigation evidence for RootIQ."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.incidents_dir = project_root / "incidents"
        self.app_dir = project_root / "app"
        self.logs_dir = project_root / "logs"

    def collect_incident_metadata(self, incident_id: str) -> str:
        """Read the incident description."""

        incident_dir = self.incidents_dir / incident_id
        readme_path = incident_dir / "README.md"

        if not readme_path.exists():
            raise FileNotFoundError(
                f"Incident not found: {incident_id}"
            )

        return readme_path.read_text()

    def collect_logs(self, incident_id: str) -> str:
        """Collect logs specific to the incident."""

        incident_log = (
            self.incidents_dir
            / incident_id
            / "application.log"
        )

        if incident_log.exists():
            return incident_log.read_text()

        log_path = self.logs_dir / "application.log"

        if not log_path.exists():
            return "No application log found."

        return log_path.read_text()

    def collect_source_code(self) -> dict:
        """Collect application source files."""

        evidence = {}

        for path in self.app_dir.glob("*.py"):
            evidence[path.name] = path.read_text()

        return evidence

    def collect_git_history(self) -> str:
        """Collect recent Git history when Git is available."""

        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--oneline",
                    "-10"
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout

        except (FileNotFoundError, subprocess.CalledProcessError):
            return "Git history unavailable in this deployment environment."


    def collect(self, incident_id: str) -> dict:
        """Collect all available investigation evidence."""

        return {
            "incident_id": incident_id,
            "incident": self.collect_incident_metadata(incident_id),
            "logs": self.collect_logs(incident_id),
            "source_code": self.collect_source_code(),
            "git_history": self.collect_git_history()
        }

    def save_bundle(self, incident_id: str, evidence: dict) -> Path:
        """Save collected evidence as a JSON bundle."""

        output_dir = (
            self.incidents_dir
            / incident_id
            / "evidence"
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "evidence_bundle.json"

        with output_path.open("w") as file:
            json.dump(evidence, file, indent=2)

        return output_path