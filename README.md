# LogGuard — Real-time Log Monitoring & Anomaly Detection

LogGuard is a Python prototype for end-to-end log management: synthetic log generation, stream processing, ML-driven anomaly detection (Isolation Forest), compressed raw-storage, and a Whoosh-based searchable index for investigations.

## Features

* **Synthetic log generation** with configurable anomaly injection
* **Continuous stream processing** of logs
* **Anomaly detection** using scikit-learn's Isolation Forest
* **Raw log compression** with zlib for efficient storage
* **Fast, searchable index** with Whoosh
* **Interactive command-line search interface** for forensic queries

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup & Installation](#setup--installation)
3. [Run the System (Three-Phase Workflow)](#run-the-system-three-phase-workflow)
4. [Optional: Live Stream Simulation](#optional--live-stream-simulation)
5. [Cleanup](#cleanup)
6. [Project Structure](#project-structure)
7. [Notes & Recommendations](#notes--recommendations)
8. [Contact](#contact)

---

## Prerequisites

* Git
* Python 3.8+
* pip (comes with Python)

---

## Setup & Installation

### Clone the repository

```bash
git clone https://github.com/akashhbais/log-monitor.git
```

### Change to project directory

```bash
cd log-monitor/logguard
```

### Create a Python virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

**On Windows (Command Prompt):**

```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**

```bash
.\venv\Scripts\Activate.ps1
```

**On Git Bash / WSL / Linux / macOS:**

```bash
source venv/bin/activate
# If your venv was created on Windows and you're using Git Bash, you may need:
# source venv/Scripts/activate
```

### Install dependencies

If the repository already contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

If you're creating `requirements.txt` yourself (after installing packages during development):

```bash
# from within the activated venv (after you pip install your packages)
pip freeze > requirements.txt
```

Common packages expected: `scikit-learn`, `pandas`, `whoosh`, etc.

---

## Run the System (Three-Phase Workflow)

Recommended: open three separate terminals (or tabs) and activate the venv in each.

### Phase 1 — Generate Initial Logs

```bash
python log_generator.py
```

Generates `data/system_logs.log`. Default generates ~50,000 records (configurable in `log_generator.py`).

Adjust `LOG_INTERVAL_SECONDS` and `NUM_LOGS_TO_GENERATE` inside the script if needed.

### Phase 2 — Process Logs & Detect Anomalies

```bash
python log_processor.py
```

Watches `data/system_logs.log`, trains an Isolation Forest model, flags anomalies, compresses raw lines, and builds/updates the Whoosh index (creates `whoosh_index/`).

Wait until it finishes the initial backfill and enters the “waiting for new logs” state before running the searcher.

### Phase 3 — Search & Investigate Logs

```bash
python log_searcher.py
```

Presents a `LogSearch >` prompt.

Example queries:

```
failed login
level:ERROR
source_ip:203.0.113.1
event_type:AUTH_ATTEMPT AND status:FAILURE
message_raw:"unauthorized access"
user*
*:*
```

Type `exit` to quit the searcher.

---

## Optional — Live Stream Simulation

To run continuously (simulate real-time logs):

Keep `log_processor.py` running (Phase 2).

In the generator (`log_generator.py`), set:

```python
NUM_LOGS_TO_GENERATE = None  # or remove limit in logic so it runs indefinitely
```

Then start the generator again:

```bash
python log_generator.py
```

`log_processor.py` will pick up new logs and process/index/analyze them in near-real-time.

---

## Cleanup

Deactivate venv, remove generated data and index:

```bash
deactivate   # in each terminal (if venv active)

# from project root
rm -rf data
rm -rf whoosh_index
rm -rf venv
```

(Windows note: use `rmdir /s /q <folder>` or delete manually.)

---

## Project Structure

```
logguard/
├── data/                  # generated logs (ignored by git)
│   └── system_logs.log
├── whoosh_index/          # whoosh index directory (ignored by git)
├── venv/                  # virtual environment (ignored by git)
├── log_generator.py       # generate synthetic logs
├── log_processor.py       # continuous processing, anomaly detection, indexing
├── log_searcher.py        # interactive search CLI
├── requirements.txt       # pip dependencies
└── README.md              # this file
```

---

## Notes & Recommendations

For larger-scale production use:

* Replace Whoosh with Elasticsearch/OpenSearch for distributed indexing and faster analytics.
* Persist compressed raw logs and metadata into object storage or a database (S3, MinIO, PostgreSQL).
* Use a streaming system like Kafka for high-throughput log ingestion.
* Use model retraining pipelines and CI/CD for safe deployment.
* Ensure logs do not contain sensitive PII in real deployments — sanitize or redact as required.

## Contact

**Akash Bais**  
[GitHub](https://github.com/akashhbais)  
[Email](mailto:akashbais41203@gmail.com)
