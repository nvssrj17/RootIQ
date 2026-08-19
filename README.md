# RootIQ — AI-Powered Incident Investigation & Root Cause Analysis

RootIQ is an evidence-driven AI incident investigation system that analyzes application incidents by combining incident metadata, application logs, source code, and Git history to identify root causes and recommend remediation steps.

Instead of relying only on log messages or isolated error traces, RootIQ builds an investigation context from multiple evidence sources and uses an AI investigator to produce a structured root-cause analysis. An evaluation layer then compares the investigation against incident-specific ground truth to measure investigation accuracy.

---

## Problem

Modern software systems generate large amounts of operational evidence across logs, source code, configuration, databases, and version-control history.

When an incident occurs, engineers often need to:

* identify the relevant logs
* understand the affected application code
* determine what changed recently
* correlate errors with application behavior
* identify the underlying root cause
* determine the appropriate remediation

This process can be time-consuming and highly dependent on manual investigation.

**RootIQ aims to automate this investigation workflow by giving an AI system structured access to the evidence an engineer would normally inspect manually.**

---

## Solution

RootIQ follows an evidence-driven investigation pipeline:

```text
Incident
   │
   ▼
Evidence Collection
   │
   ├── Incident metadata
   ├── Application logs
   ├── Source code
   └── Git history
   │
   ▼
Evidence Selection
   │
   ▼
AI Investigation
   │
   ▼
Structured Root Cause Analysis
   │
   ├── Summary
   ├── Root cause
   ├── Evidence
   ├── Files involved
   ├── Recommended fix
   └── Confidence
   │
   ▼
Ground-Truth Evaluation
   │
   ▼
Investigation Score
```

The same investigation pipeline can be accessed through the command-line interface or through the FastAPI service.

---

## Key Features

### Evidence-Driven Investigation

RootIQ collects multiple evidence sources before asking the AI investigator to determine the root cause:

* Incident description
* Application logs
* Application source code
* Recent Git history

This provides the model with contextual evidence rather than relying on a single error message.

### AI Root Cause Analysis

The investigation layer uses Groq to analyze the selected evidence and produce a structured investigation containing:

* Incident summary
* Root cause
* Supporting evidence
* Files involved
* Recommended remediation
* Confidence score

### Evidence Selection

RootIQ includes an evidence-selection layer that helps focus the investigation on the most relevant evidence before sending it to the AI model.

### Automated Evaluation

Each incident contains a ground-truth definition describing the expected root cause and remediation.

The evaluator compares the AI investigation against this ground truth and evaluates:

* Root cause correctness
* Recommended fix correctness
* Relevant files involved, when defined

The evaluator uses normalized concept-based matching rather than requiring the AI response to exactly match the wording of the ground truth.

### FastAPI Interface

RootIQ exposes the investigation pipeline through a REST API.

Available endpoints include:

```text
GET  /health
POST /investigate/{incident_id}
```

### CLI Interface

RootIQ can also be executed directly from the command line:

```bash
python -m rootiq.cli incident_001
```

---

## Architecture

```text
                    ┌──────────────────────┐
                    │       Incident       │
                    │ README + Logs + Data │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Evidence Collector  │
                    │                      │
                    │ • Metadata           │
                    │ • Application logs   │
                    │ • Source code        │
                    │ • Git history        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Evidence Selector  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    AI Investigator   │
                    │        + Groq        │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │     Structured Investigation    │
              │                                 │
              │ • Summary                       │
              │ • Root cause                    │
              │ • Evidence                      │
              │ • Files involved                │
              │ • Recommended fix               │
              │ • Confidence                    │
              └───────────────┬─────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │   RootIQ Evaluator   │
                    │                      │
                    │ AI Result vs Ground  │
                    │ Truth                │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Evaluation Score   │
                    └──────────────────────┘
```

---

## Project Structure

```text
incident_app/
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── notification.py
│   └── orders.py
│
├── incidents/
│   ├── incident_001/
│   │   ├── README.md
│   │   ├── ground_truth.json
│   │   └── evidence/
│   │       ├── evidence_bundle.json
│   │       ├── investigation_result.json
│   │       └── evaluation_result.json
│   │
│   └── incident_002/
│       ├── README.md
│       ├── ground_truth.json
│       ├── application.log
│       └── evidence/
│           ├── evidence_bundle.json
│           ├── investigation_result.json
│           └── evaluation_result.json
│
├── rootiq/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── evaluator.py
│   ├── evidence.py
│   ├── groq_client.py
│   ├── investigator.py
│   └── selector.py
│
├── logs/
│   └── application.log
│
├── requirements.txt
└── README.md
```

---

## Investigation Workflow

### 1. Incident Identification

The investigator receives an incident ID:

```text
incident_001
```

or:

```text
incident_002
```

RootIQ locates the corresponding incident directory and reads its metadata.

### 2. Evidence Collection

The `EvidenceCollector` gathers:

```text
Incident metadata
Application logs
Source code
Git history
```

The collected evidence is stored as:

```text
evidence_bundle.json
```

### 3. Evidence Selection

The evidence-selection layer identifies the information most relevant to the incident.

This reduces unnecessary context and allows the investigator to focus on the evidence that is most useful for determining the failure mechanism.

### 4. AI Investigation

The selected evidence is provided to the AI investigation layer.

The investigator produces a structured result:

```json
{
  "summary": "...",
  "root_cause": "...",
  "evidence": [],
  "files_involved": [],
  "recommended_fix": "...",
  "confidence": 0.95
}
```

### 5. Evaluation

The investigation is compared against the incident's `ground_truth.json`.

The evaluator produces:

```json
{
  "incident_id": "incident_001",
  "root_cause_correct": true,
  "fix_correct": true,
  "files_correct": null,
  "score": 1.0
}
```

---

# Incident Scenarios

## Incident 001 — Database Schema Mismatch

### Symptom

The Orders API returns:

```text
HTTP 500
```

when retrieving an order.

### Root Cause

The SQLAlchemy `Order` model expects a `customer_email` column, but the existing SQLite `orders` table does not contain that column.

This creates a database schema mismatch between the application model and the actual database schema.

### Evidence

RootIQ identifies evidence including:

```text
sqlite3.OperationalError:
no such column: orders.customer_email
```

and the corresponding model definition:

```text
customer_email = Column(String, nullable=False)
```

### Recommended Fix

Synchronize the database schema with the model definition by applying the required migration or recreating the database in the demonstration environment.

### Evaluation

```text
Root Cause:       PASS
Recommended Fix:  PASS
Overall Score:    1.00
```

---

## Incident 002 — Order Notification Service Failure

### Symptom

Order creation succeeds, but the notification step fails and the API returns:

```text
HTTP 500
```

### Root Cause

The `NOTIFICATION_URL` environment variable was configured to point to:

```text
localhost:9999/notify
```

where no notification service was running.

This resulted in a connection-refused error.

### Evidence

RootIQ identified:

```text
requests.exceptions.ConnectionError
```

and:

```text
HTTPConnectionPool(host='localhost', port=9999)
```

The investigation also traced the notification request to:

```text
notification.py
```

and the order endpoint to:

```text
orders.py
```

### Recommended Fix

Configure `NOTIFICATION_URL` to point to the correct reachable notification service endpoint and verify the service is available before deployment.

### Evaluation

```text
Root Cause:       PASS
Recommended Fix:  PASS
Files Involved:   PASS
Overall Score:    1.00
```

---

# Evaluation Results

RootIQ has currently been validated against two intentionally constructed incidents:

| Incident                                    | Root Cause |  Fix | Files |    Score |
| ------------------------------------------- | ---------: | ---: | ----: | -------: |
| Incident 001 — Database Schema Mismatch     |       PASS | PASS |   N/A | **1.00** |
| Incident 002 — Notification Service Failure |       PASS | PASS |  PASS | **1.00** |

The evaluation framework is designed to make investigation quality measurable instead of relying solely on subjective inspection of AI responses.

---

# API

RootIQ provides a FastAPI interface.

## Start the API Locally

From the project root:

```bash
uvicorn rootiq.api:app --app-dir incident_app --reload
```

The service runs locally at:

```text
http://127.0.0.1:8000
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "RootIQ"
}
```

## Investigate an Incident

```bash
curl -X POST http://127.0.0.1:8000/investigate/incident_001
```

The endpoint returns both the investigation and its evaluation:

```json
{
  "incident_id": "incident_001",
  "investigation": {
    "summary": "...",
    "root_cause": "...",
    "evidence": [],
    "files_involved": [],
    "recommended_fix": "...",
    "confidence": 0.95
  },
  "evaluation": {
    "incident_id": "incident_001",
    "root_cause_correct": true,
    "fix_correct": true,
    "files_correct": null,
    "score": 1.0
  }
}
```

---

# CLI Usage

RootIQ can also be executed without the API.

From the project root:

```bash
python -m rootiq.cli incident_001
```

or:

```bash
python -m rootiq.cli incident_002
```

The CLI displays:

* Investigation summary
* Root cause
* Supporting evidence
* Files involved
* Recommended fix
* Confidence
* Evaluation results

---

# Local Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd RootIQ
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r incident_app/requirements.txt
```

## 4. Configure Environment Variables

Create a local `.env` file:

```text
GROQ_API_KEY=your_api_key_here
```

The `.env` file should never be committed to source control.

## 5. Run RootIQ

CLI:

```bash
python -m rootiq.cli incident_001
```

API:

```bash
uvicorn rootiq.api:app --app-dir incident_app --reload
```

---

# Environment Variables

RootIQ requires:

| Variable       | Description                     |
| -------------- | ------------------------------- |
| `GROQ_API_KEY` | API key used by the Groq client |

For local development, these values can be stored in `.env`.

For deployment, environment variables should be configured through the hosting platform's secret/environment-variable management rather than committing them to the repository.

---

# Deployment

**Live Vercel Deployment**

RootIQ is deployed as a live FastAPI application on Vercel.

Production API

Live API:
https://rootiq-ai.vercel.app

Interactive API Documentation:
https://rootiq-ai.vercel.app/docs

Health Check:
https://rootiq-ai.vercel.app/health

GitHub Repository:
https://github.com/nvssrj17/RootIQ

Production Investigation

curl -X POST https://rootiq-ai.vercel.app/investigate/incident_001

or:

curl -X POST https://rootiq-ai.vercel.app/investigate/incident_002

**Vercel Deployment Configuration**

The Vercel configuration is defined in:

incident_app/vercel.json

The application uses the Vercel Python runtime to expose the FastAPI application.

The deployed API provides:

GET  /
GET  /health
POST /investigate/{incident_id}

**Environment Variables**

RootIQ requires:

GROQ_API_KEY

For local development, the key can be stored in:

.env

For production, the key is configured through Vercel environment-variable management.

Secrets are not committed to the repository.

**Vercel Deployment Considerations**

During deployment, two differences between the local environment and Vercel's serverless runtime were identified.

**Git Availability**

The local implementation can execute:

git log --oneline -10

to collect recent Git history.

The Vercel runtime does not provide the local Git executable in the same way.

RootIQ was therefore designed so Git history is optional evidence.

Local Environment
       ↓
Git Available
       ↓
Git History Included

while:

Vercel
   ↓
Git Unavailable
   ↓
Investigation Continues

The absence of Git no longer causes the entire investigation to fail.

**Read-Only Filesystem**

Locally, RootIQ can save:

investigation_result.json
evaluation_result.json

inside the incident evidence directory.

Vercel's deployed serverless filesystem is read-only, so attempting to write these files caused runtime failures.

RootIQ was adapted so that:

Local Environment
    ↓
Investigate
    ↓
Evaluate
    ↓
Save JSON artifacts
    ↓
Return result

while on Vercel:

Vercel
   ↓
Investigate
   ↓
Evaluate
   ↓
Return JSON response

The investigation and evaluation logic remains the same; only filesystem persistence is environment-dependent.

---

# Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn

### AI

* Groq API
* Evidence-driven investigation workflow

### Data & Application

* SQLAlchemy
* SQLite
* Python logging

### Investigation

* Structured evidence collection
* Source-code inspection
* Log analysis
* Git history analysis
* Evidence selection

### Evaluation

* Ground-truth incident definitions
* Concept-based root-cause matching
* Recommended-fix evaluation
* File involvement evaluation

### Deployment

* Render
* Environment-based configuration

---

# Design Principles

## Evidence Before Explanation

RootIQ does not ask the AI to diagnose an incident from a short description alone. It first collects the evidence an engineer would normally inspect.

## Structured Output

The investigation result follows a predictable structure, making the output easier to consume programmatically.

## Measurable Accuracy

Ground truth and automated evaluation provide an objective mechanism for measuring whether the investigation reached the expected conclusion.

## Separation of Investigation and Evaluation

The investigator produces the diagnosis, while a separate evaluator determines whether the diagnosis aligns with the expected result.

This separation helps prevent the investigation process from determining its own correctness.

---

# Current Limitations

RootIQ is currently a focused prototype demonstrating evidence-driven incident investigation.

Current limitations include:

* The evaluation dataset contains two incident scenarios.
* Ground truth is manually defined for each incident.
* The investigation currently operates on a local evidence structure.
* The system relies on an external Groq API for AI reasoning.
* The current API does not provide authentication or rate limiting.
* Production observability and persistent investigation storage have not yet been implemented.

These limitations provide opportunities for future development.

---

# Future Enhancements

Potential future improvements include:

* Larger incident benchmark datasets
* Retrieval-augmented investigation across historical incidents
* Automated incident clustering
* More advanced semantic evaluation
* Timeline reconstruction from Git and logs
* Automated remediation generation
* Incident similarity search
* Persistent investigation history
* Authentication and authorization
* Production monitoring and observability
* Web-based investigation dashboard
* Integration with incident-management and alerting platforms

---

# Project Status

**RootIQ is currently a working prototype with an operational CLI, FastAPI investigation API, automated evaluation framework, and two validated incident scenarios.**

Current validation:

```text
Incident 001 → 1.00
Incident 002 → 1.00
```

The next stage is deployment and validation of the public API endpoint.
