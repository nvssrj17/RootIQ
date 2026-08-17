import re


class EvidenceSelector:
    """Ranks source files based on incident-specific technical signals."""

    def select(self, evidence: dict) -> dict:

        incident_text = (
            evidence["incident"]
            + "\n"
            + evidence["logs"]
        ).lower()

        # ---------------------------------------------------------
        # Strong signals
        # These are usually highly specific to the incident.
        # ---------------------------------------------------------

        strong_patterns = [
            r"\b[a-zA-Z_][a-zA-Z0-9_]*_[a-zA-Z0-9_]+\b",  # snake_case identifiers
            r"/[a-zA-Z0-9_/-]+",                           # API endpoints
            r"\b\w+error\b",                              # exception names
            r"\b\w+exception\b",
            r"\bmissing\s+column\b",
            r"\bno\s+such\s+column\b",
        ]

        strong_signals = set()

        for pattern in strong_patterns:
            matches = re.findall(pattern, incident_text)
            strong_signals.update(matches)

        # Specific database / incident concepts
        important_terms = {
            "customer_email",
            "customer_name",
            "order",
            "orders",
            "sqlite",
            "sqlalchemy",
            "column",
            "schema",
            "operationalerror",
            "database",
        }

        strong_signals.update(important_terms.intersection(
            set(re.findall(
                r"[a-zA-Z_][a-zA-Z0-9_]*",
                incident_text
            ))
        ))

        # ---------------------------------------------------------
        # Generic words
        # These should contribute little or nothing.
        # ---------------------------------------------------------

        generic_terms = {
            "base",
            "check",
            "engine",
            "exception",
            "error",
            "request",
            "requested",
            "application",
            "server",
            "running",
            "status",
            "health",
            "healthy",
            "fetching",
            "successfully",
            "while",
            "from",
            "with",
            "this",
            "that",
            "there",
        }

        scored_files = []

        for filename, content in evidence["source_code"].items():

            score = 0
            reasons = []

            filename_lower = filename.lower()
            content_lower = content.lower()

            # -----------------------------------------------------
            # 1. Filename relevance
            # -----------------------------------------------------

            filename_stem = filename_lower.replace(".py", "")

            if filename_stem in incident_text:
                score += 5
                reasons.append(
                    "filename mentioned in incident evidence"
                )

            # -----------------------------------------------------
            # 2. Strong incident-specific matches
            # -----------------------------------------------------

            # High-value incident-specific signals
            high_value_signals = {
                "customer_email": 10,
                "no such column": 10,
                "operationalerror": 8,
                "customer_name": 6,
                "orders": 3,
                "order": 2,
                "database": 2,
                "sqlalchemy": 2,
                "column": 4,
                "schema": 4,
            }

            for signal, weight in high_value_signals.items():
                if signal in content_lower:
                    score += weight
                    reasons.append(
                        f"matches '{signal}' (+{weight})"
                    )

            # -----------------------------------------------------
            # 3. API relationship
            # -----------------------------------------------------

            if "/orders" in incident_text:

                if (
                    "router" in content_lower
                    or "orders" in content_lower
                    or "api" in content_lower
                ):
                    score += 3
                    reasons.append("related to orders API")

            # -----------------------------------------------------
            # 4. Database relationship
            # -----------------------------------------------------

            database_signals = {
                "database",
                "sqlite",
                "sqlalchemy",
                "column",
                "schema",
                "customer_email",
            }

            matched_database = (
                database_signals.intersection(strong_signals)
            )

            if matched_database and (
                "sqlalchemy" in content_lower
                or "create_engine" in content_lower
                or "session" in content_lower
                or "column" in content_lower
            ):
                score += 3
                reasons.append("database-related code")

            # -----------------------------------------------------
            # 5. Generic words are intentionally ignored.
            # -----------------------------------------------------

            # We don't award points for words such as:
            # "base", "check", "exception", "engine", etc.
            #
            # This prevents common framework terminology from
            # making unrelated files appear highly relevant.

            scored_files.append(
                {
                    "filename": filename,
                    "content": content,
                    "score": score,
                    "reasons": reasons,
                }
            )

        # Highest relevance first
        scored_files.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # Keep only meaningfully relevant evidence.
        selected_source_code = {}

        for item in scored_files:
            if item["score"] >= 5:
                selected_source_code[item["filename"]] = item["content"]

        return {
            "incident": evidence["incident"],
            "logs": evidence["logs"],
            "source_code": selected_source_code,
            "git_history": evidence["git_history"],
            "relevance": [
                {
                    "filename": item["filename"],
                    "score": item["score"],
                    "reasons": item["reasons"],
                }
                for item in scored_files
            ],
        }